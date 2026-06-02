import asyncio
import hashlib
import hmac
import logging
import sys
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import PlainTextResponse

sys.path.insert(0, str(Path(__file__).parent))
import agent
import config
import db

log = logging.getLogger("agenty.webhook")

router = APIRouter()


@router.get("/webhook/whatsapp", response_class=PlainTextResponse)
async def whatsapp_verify(
    hub_mode:         str = None,
    hub_verify_token: str = None,
    hub_challenge:    str = None,
):
    """Verificação do webhook pelo Meta."""
    if hub_mode == "subscribe" and hub_verify_token == config.WA_VERIFY_TOKEN:
        log.info("Webhook Meta verificado com sucesso")
        return hub_challenge
    raise HTTPException(status_code=403, detail="Token inválido")


@router.post("/webhook/whatsapp")
async def whatsapp_receive(request: Request,
                           x_hub_signature_256: str = Header(None)):
    payload = await request.body()

    # Verifica assinatura HMAC
    if x_hub_signature_256:
        expected = "sha256=" + hmac.new(
            config.WA_VERIFY_TOKEN.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, x_hub_signature_256):
            raise HTTPException(status_code=403, detail="Assinatura inválida")

    data = await request.json()

    # Processa cada entry em background para responder 200 imediatamente ao Meta
    asyncio.create_task(_process_payload(data))
    return {"status": "ok"}


async def _process_payload(data: dict):
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                _handle_value(value)
    except Exception as e:
        log.error(f"Erro ao processar payload: {e}")


def _handle_value(value: dict):
    phone_number_id = value.get("metadata", {}).get("phone_number_id", "")
    messages        = value.get("messages", [])

    if not messages or not phone_number_id:
        return

    client = db.get_client_by_phone_number_id(phone_number_id)
    if not client:
        log.warning(f"Nenhum cliente ativo encontrado para phone_number_id={phone_number_id}")
        return

    for msg in messages:
        _handle_message(msg, client)


def _handle_message(msg: dict, client: dict):
    wa_message_id = msg.get("id", "")
    customer      = msg.get("from", "")
    msg_type      = msg.get("type", "")

    # Só processa mensagens de texto
    if msg_type != "text":
        log.info(f"Mensagem ignorada (tipo={msg_type})")
        return

    text = msg.get("text", {}).get("body", "").strip()
    if not text:
        return

    # Deduplicação — Meta pode reenviar webhooks
    if wa_message_id and db.is_duplicate_message(wa_message_id):
        log.info(f"Mensagem duplicada ignorada: {wa_message_id}")
        return

    # Marcar como lida
    db.mark_read_flag = True
    wa_client_mod = __import__("wa_client")
    wa_client_mod.mark_read(client["phone_number_id"], client["access_token"], wa_message_id)

    # Criar/recuperar conversa
    conversation = db.get_or_create_conversation(client["id"], customer)

    # Salvar mensagem do usuário
    db.save_message(conversation["id"], "user", text, wa_message_id)
    message_count = db.increment_message_count(conversation["id"])

    # Atualiza o message_count no objeto para o agent usar
    conversation["message_count"] = message_count

    log.info(f"[{client.get('biz_name', client['id'])}] Mensagem de {customer}: {text[:60]}")

    # Orquestra resposta
    agent.respond(client, conversation, text)
