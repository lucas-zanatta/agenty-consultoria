import logging
import smtplib
import sys
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent))
import config
import db
import wa_client

log = logging.getLogger("agenty.tools")

_CAL_BASE = "https://api.cal.com/v1"

# Definições de tools para a API do Claude
TOOL_DEFINITIONS = [
    {
        "name": "capture_lead",
        "description": (
            "Use quando o cliente demonstrar interesse real em um serviço/produto "
            "e você tiver coletado informações suficientes. "
            "Registra o lead e notifica o dono do negócio."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string", "description": "Nome do cliente"},
                "interest":      {"type": "string", "description": "O que o cliente quer/precisa"},
                "budget":        {"type": "string", "description": "Orçamento mencionado pelo cliente (se houver)"},
            },
            "required": ["customer_name", "interest"],
        },
    },
    {
        "name": "check_slots",
        "description": "Verifica horários disponíveis para agendamento em uma data específica.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Data desejada no formato YYYY-MM-DD"},
            },
            "required": ["date"],
        },
    },
    {
        "name": "book_appointment",
        "description": "Agenda um horário para o cliente após ele confirmar data e hora.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_name":  {"type": "string"},
                "customer_phone": {"type": "string"},
                "date_time":      {"type": "string", "description": "Data e hora no formato ISO 8601"},
                "notes":          {"type": "string", "description": "Observações adicionais (opcional)"},
            },
            "required": ["customer_name", "customer_phone", "date_time"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": (
            "Use quando: (1) o cliente pedir explicitamente para falar com atendente, "
            "(2) a dúvida for muito complexa para o bot, "
            "(3) houver reclamação grave ou situação sensível."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "Motivo da escalada"},
            },
            "required": ["reason"],
        },
    },
]


def execute_tool(tool_name: str, tool_input: dict,
                 client: dict, conversation: dict) -> str:
    """Executa a tool chamada pelo Claude e retorna o resultado como string."""
    if tool_name == "capture_lead":
        return _capture_lead(tool_input, client, conversation)
    if tool_name == "check_slots":
        return _check_slots(tool_input, client)
    if tool_name == "book_appointment":
        return _book_appointment(tool_input, client, conversation)
    if tool_name == "escalate_to_human":
        return _escalate(tool_input, client, conversation)
    return f"Tool '{tool_name}' não reconhecida."


def _capture_lead(inp: dict, client: dict, conversation: dict) -> str:
    name     = inp.get("customer_name", "")
    interest = inp.get("interest", "")
    budget   = inp.get("budget", "")

    lead_data = {"name": name, "interest": interest, "budget": budget,
                 "captured_at": datetime.now(timezone.utc).isoformat()}
    db.save_lead(conversation["id"], lead_data)
    if name:
        db.update_customer_name(conversation["id"], name)

    # Notifica o dono por e-mail
    _notify_lead_email(client, conversation["customer_phone"], lead_data)

    # Notifica por WhatsApp se houver handover_phone configurado
    if client.get("handover_phone") and client.get("phone_number_id"):
        msg = (
            f"Novo lead capturado!\n"
            f"Nome: {name}\n"
            f"Interesse: {interest}\n"
            f"Orçamento: {budget or 'não informado'}\n"
            f"WhatsApp: {conversation['customer_phone']}"
        )
        wa_client.send_message(
            client["phone_number_id"],
            client["access_token"],
            client["handover_phone"],
            msg,
        )

    log.info(f"Lead capturado: {name} — {interest}")
    return f"Lead registrado com sucesso para {name}."


def _check_slots(inp: dict, client: dict) -> str:
    if not client.get("cal_api_key") or not client.get("cal_event_type_id"):
        return "Agendamento online não está configurado. Por favor, entre em contato diretamente."

    date = inp.get("date", "")
    try:
        start = f"{date}T00:00:00Z"
        end   = f"{date}T23:59:59Z"
        params = {
            "apiKey":      client["cal_api_key"],
            "eventTypeId": client["cal_event_type_id"],
            "startTime":   start,
            "endTime":     end,
        }
        with httpx.Client(timeout=15) as http:
            resp = http.get(f"{_CAL_BASE}/slots/available", params=params)
        resp.raise_for_status()
        slots = resp.json().get("slots", {})

        day_slots = slots.get(date, [])
        if not day_slots:
            return f"Não há horários disponíveis em {date}."

        times = [s["time"][11:16] for s in day_slots[:8]]
        return f"Horários disponíveis em {date}: {', '.join(times)}."
    except Exception as e:
        log.error(f"Erro ao verificar slots Cal.com: {e}")
        return "Não consegui verificar a disponibilidade agora. Tente novamente em instantes."


def _book_appointment(inp: dict, client: dict, conversation: dict) -> str:
    if not client.get("cal_api_key") or not client.get("cal_event_type_id"):
        return "Agendamento online não está configurado. Entre em contato diretamente."

    try:
        payload = {
            "apiKey":      client["cal_api_key"],
            "eventTypeId": int(client["cal_event_type_id"]),
            "start":       inp["date_time"],
            "responses": {
                "name":  inp["customer_name"],
                "email": f"{inp['customer_phone']}@whatsapp.placeholder",
                "smsReminderNumber": inp["customer_phone"],
                "notes": inp.get("notes", ""),
            },
            "timeZone": client.get("timezone", "America/Sao_Paulo"),
            "language": "pt-BR",
        }
        with httpx.Client(timeout=20) as http:
            resp = http.post(f"{_CAL_BASE}/bookings", json=payload)
        resp.raise_for_status()
        data = resp.json()
        uid = data.get("uid", "")
        log.info(f"Agendamento criado: {uid}")
        return (
            f"Agendamento confirmado para {inp['customer_name']} "
            f"em {inp['date_time'][:16].replace('T', ' às ')}. "
            f"Você receberá uma confirmação em breve."
        )
    except Exception as e:
        log.error(f"Erro ao criar agendamento: {e}")
        return "Não consegui confirmar o agendamento. Por favor, tente novamente ou entre em contato diretamente."


def _escalate(inp: dict, client: dict, conversation: dict) -> str:
    reason = inp.get("reason", "")
    db.set_conversation_handed_over(conversation["id"])

    # Notifica dono via WhatsApp
    if client.get("handover_phone") and client.get("phone_number_id"):
        msg = (
            f"Atendimento para revisão humana\n"
            f"Cliente: {conversation['customer_phone']}\n"
            f"Motivo: {reason}"
        )
        wa_client.send_message(
            client["phone_number_id"],
            client["access_token"],
            client["handover_phone"],
            msg,
        )

    log.info(f"Escalada para humano: {conversation['customer_phone']} — {reason}")
    return "Transferência para atendente registrada."


def _notify_lead_email(client: dict, customer_phone: str, lead: dict):
    if not config.SMTP_USER or not client.get("email"):
        return
    try:
        subject = f"[Agenty] Novo lead — {client.get('biz_name', client['email'])}"
        body = (
            f"Nome: {lead.get('name', '')}\n"
            f"Interesse: {lead.get('interest', '')}\n"
            f"Orçamento: {lead.get('budget', 'não informado')}\n"
            f"WhatsApp: {customer_phone}\n"
        )
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"]    = f"Agenty <{config.SMTP_USER}>"
        msg["To"]      = client["email"]
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_USER, client["email"], msg.as_string())
    except Exception as e:
        log.error(f"Falha ao enviar e-mail de lead: {e}")
