import logging
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import stripe
from fastapi import APIRouter, Header, HTTPException, Request

sys.path.insert(0, str(Path(__file__).parent))
import config
import db

log = logging.getLogger("agenty.stripe")

router = APIRouter()
stripe.api_key = config.STRIPE_SECRET_KEY


@router.post("/webhook/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, config.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Assinatura inválida")

    if event["type"] == "checkout.session.completed":
        _handle_checkout(event["data"]["object"])
    elif event["type"] == "customer.subscription.deleted":
        _handle_subscription_deleted(event["data"]["object"])

    return {"received": True}


def _handle_checkout(session: dict):
    email    = session.get("customer_details", {}).get("email", "")
    name     = session.get("customer_details", {}).get("name", "")
    cust_id  = session.get("customer", "")
    sub_id   = session.get("subscription", "")

    if not email:
        log.warning("checkout.session.completed sem e-mail")
        return

    log.info(f"Novo cliente WhatsApp via Stripe: {email}")
    client = db.create_client_record(email=email, name=name,
                                     stripe_customer_id=cust_id,
                                     stripe_subscription_id=sub_id)
    _send_onboarding_email(email, name, str(client["onboarding_token"]))


def _handle_subscription_deleted(subscription: dict):
    cust_id = subscription.get("customer", "")
    if not cust_id:
        return
    from supabase import create_client as sb_create
    _sb = sb_create(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
    result = _sb.table("wa_clients").select("id").eq("stripe_customer_id", cust_id).execute()
    if result.data:
        db.suspend_client(result.data[0]["id"])
        log.info(f"Cliente WhatsApp suspenso: {cust_id}")


def _send_onboarding_email(email: str, name: str, token: str):
    onboarding_url = f"{config.APP_BASE_URL}/onboarding/{token}"
    first = name.split()[0] if name else "cliente"

    subject = "[Agenty] Configure o Zinvo em 5 minutos"
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:32px 16px">
<table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden">
  <tr><td style="background:#080812;padding:24px 32px">
    <p style="margin:0;color:#c94a1f;font-size:22px;font-weight:bold;font-family:Arial,sans-serif">Agenty</p>
    <p style="margin:4px 0 0;color:#64748b;font-size:13px">Zinvo — Atendente WhatsApp Inteligente</p>
  </td></tr>
  <tr><td style="padding:32px">
    <h2 style="margin:0 0 16px;color:#0f172a">Olá, {first}!</h2>
    <p style="margin:0 0 16px;color:#334155;line-height:1.7">
      O Zinvo — seu atendente WhatsApp inteligente — está pronto para ser configurado. Leva menos de 5 minutos.
    </p>
    <div style="text-align:center;margin:28px 0">
      <a href="{onboarding_url}"
         style="display:inline-block;background:#c94a1f;color:#fff;padding:16px 40px;
                border-radius:8px;text-decoration:none;font-weight:bold;font-size:16px">
        Configurar o Zinvo
      </a>
    </div>
    <p style="margin:0;color:#94a3b8;font-size:13px">
      Este link é único para você e expira em 7 dias.<br>
      Qualquer dúvida, responda este e-mail.
    </p>
  </td></tr>
  <tr><td style="background:#f8fafc;padding:16px 32px;border-top:1px solid #e2e8f0;text-align:center">
    <p style="margin:0;color:#94a3b8;font-size:12px">
      Agenty — Sua empresa fatura mais com IA &nbsp;·&nbsp;
      <a href="https://agenty.com.br" style="color:#c94a1f;text-decoration:none">agenty.com.br</a>
    </p>
  </td></tr>
</table></td></tr></table>
</body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Agenty <{config.SMTP_USER}>"
    msg["To"]      = email
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_USER, email, msg.as_string())
        log.info(f"E-mail de onboarding WhatsApp enviado para {email}")
    except Exception as e:
        log.error(f"Falha ao enviar e-mail: {e}")
