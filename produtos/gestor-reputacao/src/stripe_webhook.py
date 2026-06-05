import logging
import sys
from pathlib import Path

import stripe
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

sys.path.insert(0, str(Path(__file__).parent))
import config
import db
import notifier

log = logging.getLogger("agenty.stripe")
router = APIRouter()
stripe.api_key = config.STRIPE_SECRET_KEY

_SUCCESS_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Pagamento confirmado — Agenty</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:Arial,sans-serif;background:#080812;color:#faf7f2;
         display:flex;align-items:center;justify-content:center;min-height:100vh;padding:24px}
    .box{max-width:480px;text-align:center}
    .logo{color:#c94a1f;font-size:26px;font-weight:bold;letter-spacing:.08em;margin-bottom:40px}
    h1{font-size:2rem;margin-bottom:16px;line-height:1.2}
    p{color:rgba(250,247,242,.65);line-height:1.7;margin-bottom:28px;font-size:1.05rem}
    .badge{display:inline-block;background:rgba(45,122,79,.15);border:1px solid rgba(45,122,79,.4);
           color:#2d7a4f;padding:10px 24px;border-radius:999px;font-size:.9rem}
    .back{display:block;margin-top:36px;color:rgba(250,247,242,.35);font-size:.85rem;text-decoration:none}
    .back:hover{color:rgba(250,247,242,.65)}
  </style>
</head>
<body>
  <div class="box">
    <div class="logo">AGENTY</div>
    <h1>Pagamento confirmado!</h1>
    <p>O link de configuração foi enviado para o seu e-mail.<br>
       Leva menos de 5 minutos para ativar sua automação.</p>
    <span class="badge">Verifique a caixa de entrada (e o spam)</span>
    <a href="https://agenty.com.br" class="back">← Voltar para agenty.com.br</a>
  </div>
</body>
</html>"""


@router.get("/checkout")
async def start_checkout():
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": config.STRIPE_PRICE_ID, "quantity": 1}],
        success_url=f"{config.APP_BASE_URL}/checkout/success",
        cancel_url="https://agenty.com.br/gestor-reputacao.html",
        allow_promotion_codes=True,
        billing_address_collection="auto",
    )
    return RedirectResponse(session.url, status_code=303)


@router.get("/checkout/success", response_class=HTMLResponse)
async def checkout_success():
    return HTMLResponse(_SUCCESS_HTML)


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
    email   = session.get("customer_details", {}).get("email", "")
    name    = session.get("customer_details", {}).get("name", "")
    cust_id = session.get("customer", "")
    sub_id  = session.get("subscription", "")

    if not email:
        log.warning("checkout.session.completed sem e-mail")
        return

    log.info(f"Novo cliente Gestor de Reputacao: {email}")
    client = db.create_client_record(
        email=email, name=name,
        stripe_customer_id=cust_id,
        stripe_subscription_id=sub_id,
    )
    notifier.send_onboarding_email(email, name, str(client["onboarding_token"]))


def _handle_subscription_deleted(subscription: dict):
    cust_id = subscription.get("customer", "")
    if not cust_id:
        return
    from supabase import create_client as sb_create
    _sb = sb_create(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
    result = _sb.table("clients").select("id").eq("stripe_customer_id", cust_id).execute()
    if result.data:
        db.suspend_client(result.data[0]["id"])
        log.info(f"Cliente Gestor de Reputacao suspenso: {cust_id}")
