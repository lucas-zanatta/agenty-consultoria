import logging
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import anthropic

sys.path.insert(0, str(Path(__file__).parent))
import config
import db
import rag
import tools
import wa_client

log = logging.getLogger("agenty.agent")

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def _build_system_prompt(client: dict, rag_context: str) -> str:
    biz = client.get("biz_name") or client.get("email", "este negócio")
    biz_type = client.get("biz_type", "empresa")
    biz_city = client.get("biz_city", "Curitiba")

    sections = [
        f"Você é o atendente virtual de {biz}, {biz_type} em {biz_city}.",
        "Idioma: Português brasileiro. Tom: prestativo, cordial e direto.",
        "Nunca invente informações — se não souber, diga que vai verificar e peça para o cliente aguardar.",
        "Responda em no máximo 3 parágrafos curtos. Use quebras de linha para facilitar a leitura no WhatsApp.",
    ]

    if client.get("biz_services"):
        sections.append(f"\nServiços / Produtos:\n{client['biz_services']}")
    if client.get("biz_prices"):
        sections.append(f"\nPreços:\n{client['biz_prices']}")
    if client.get("biz_address"):
        sections.append(f"\nEndereço / Área de atendimento: {client['biz_address']}")
    if client.get("biz_payment_methods"):
        sections.append(f"\nFormas de pagamento: {client['biz_payment_methods']}")
    if client.get("biz_cancellation"):
        sections.append(f"\nPolítica de cancelamento: {client['biz_cancellation']}")
    if client.get("biz_differentials"):
        sections.append(f"\nDiferenciais: {client['biz_differentials']}")
    if client.get("biz_extra"):
        sections.append(f"\nInformações adicionais: {client['biz_extra']}")

    if rag_context:
        sections.append(f"\nInformações dos documentos do negócio:\n{rag_context}")

    return "\n".join(sections)


def _is_within_hours(client: dict) -> bool:
    tz_name = client.get("timezone") or "America/Sao_Paulo"
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("America/Sao_Paulo")
    now = datetime.now(tz)
    start = client.get("business_hours_start") or 8
    end   = client.get("business_hours_end") or 18
    return start <= now.hour < end


def _check_handover_keywords(message: str, client: dict) -> bool:
    keywords = client.get("handover_keywords") or ["atendente", "humano", "pessoa"]
    msg_lower = message.lower()
    return any(kw.lower() in msg_lower for kw in keywords)


def respond(client: dict, conversation: dict, user_message: str):
    """Orquestra a resposta completa para uma mensagem do cliente."""
    phone_id     = client["phone_number_id"]
    access_token = client["access_token"]
    customer     = conversation["customer_phone"]

    # Fora do horário comercial
    if not _is_within_hours(client):
        out_msg = (
            client.get("out_of_hours_message")
            or "Olá! No momento estamos fora do horário de atendimento. "
               "Retornaremos em breve. Obrigado!"
        )
        wa_client.send_message(phone_id, access_token, customer, out_msg)
        db.save_message(conversation["id"], "assistant", out_msg)
        return

    # Limite de mensagens automáticas atingido
    max_msgs = client.get("max_auto_messages") or 10
    if conversation.get("message_count", 0) >= max_msgs:
        _auto_escalate(client, conversation, "Limite de mensagens automáticas atingido")
        return

    # Palavra-chave de escalada detectada
    if _check_handover_keywords(user_message, client):
        _auto_escalate(client, conversation, "Cliente solicitou atendimento humano")
        return

    # Conversa já escalada
    if conversation.get("status") == "handed_over":
        return

    # RAG — busca contexto nos documentos do cliente
    rag_context = rag.get_relevant_context(client["id"], user_message)

    # Histórico recente
    history = db.get_recent_messages(conversation["id"], limit=10)
    messages = [{"role": m["role"], "content": m["content"]} for m in history]

    system_prompt = _build_system_prompt(client, rag_context)

    try:
        response = _client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system=system_prompt,
            tools=tools.TOOL_DEFINITIONS,
            messages=messages,
        )
    except Exception as e:
        log.error(f"Erro ao chamar Claude: {e}")
        wa_client.send_message(phone_id, access_token, customer,
                               "Desculpe, estou com uma instabilidade. Tente novamente em instantes.")
        return

    # Processa tools e resposta
    reply_text = _process_response(response, client, conversation, messages, system_prompt)

    if reply_text:
        wa_client.send_message(phone_id, access_token, customer, reply_text)
        db.save_message(conversation["id"], "assistant", reply_text)


def _process_response(response, client: dict, conversation: dict,
                      messages: list, system_prompt: str) -> str:
    """Processa a resposta do Claude, executa tools se necessário e retorna o texto final."""
    phone_id     = client["phone_number_id"]
    access_token = client["access_token"]
    customer     = conversation["customer_phone"]

    # Resposta direta sem tool use
    if response.stop_reason == "end_turn":
        for block in response.content:
            if hasattr(block, "text"):
                return block.text.strip()
        return ""

    # Tool use
    if response.stop_reason == "tool_use":
        tool_results = []
        reply_text = ""

        for block in response.content:
            if block.type == "tool_use":
                result = tools.execute_tool(block.name, block.input, client, conversation)
                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     result,
                })
            elif hasattr(block, "text") and block.text:
                reply_text = block.text.strip()

        # Segunda chamada ao Claude com os resultados das tools
        if tool_results:
            try:
                messages_with_tools = messages + [
                    {"role": "assistant", "content": response.content},
                    {"role": "user",      "content": tool_results},
                ]
                response2 = _client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=500,
                    system=system_prompt,
                    tools=tools.TOOL_DEFINITIONS,
                    messages=messages_with_tools,
                )
                for block in response2.content:
                    if hasattr(block, "text") and block.text:
                        reply_text = block.text.strip()
            except Exception as e:
                log.error(f"Erro na segunda chamada ao Claude: {e}")

        return reply_text

    return ""


def _auto_escalate(client: dict, conversation: dict, reason: str):
    """Escalada automática para humano."""
    result = tools.execute_tool("escalate_to_human", {"reason": reason}, client, conversation)
    msg = (
        "Vou transferir você para um de nossos atendentes. "
        "Em breve alguém entrará em contato. Obrigado pela paciência!"
    )
    wa_client.send_message(
        client["phone_number_id"], client["access_token"],
        conversation["customer_phone"], msg,
    )
    db.save_message(conversation["id"], "assistant", msg)
