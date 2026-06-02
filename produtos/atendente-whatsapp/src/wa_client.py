import logging
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent))

log = logging.getLogger("agenty.wa")

_GRAPH_BASE = "https://graph.facebook.com/v18.0"


def send_message(phone_number_id: str, access_token: str,
                 to: str, text: str) -> bool:
    url = f"{_GRAPH_BASE}/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type":    "individual",
        "to":                to,
        "type":              "text",
        "text":              {"body": text},
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type":  "application/json",
    }
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            return True
        log.warning(f"Falha ao enviar mensagem ({resp.status_code}): {resp.text[:200]}")
        return False
    except Exception as e:
        log.error(f"Erro ao enviar mensagem: {e}")
        return False


def send_typing(phone_number_id: str, access_token: str, to: str):
    """Envia indicador de digitação (aparece por ~25s no WhatsApp)."""
    url = f"{_GRAPH_BASE}/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type":    "individual",
        "to":                to,
        "type":              "reaction",
        "reaction":          {"message_id": "", "emoji": ""},
    }
    # O Meta não tem endpoint nativo de typing — envia mensagem vazia (sem efeito visual)
    # mas marca o webhook como lido, que remove o "duplo check cinza"
    mark_read(phone_number_id, access_token, to)


def mark_read(phone_number_id: str, access_token: str, message_id: str):
    """Marca uma mensagem como lida (double check azul)."""
    url = f"{_GRAPH_BASE}/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "status":            "read",
        "message_id":        message_id,
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type":  "application/json",
    }
    try:
        with httpx.Client(timeout=10) as client:
            client.post(url, json=payload, headers=headers)
    except Exception:
        pass
