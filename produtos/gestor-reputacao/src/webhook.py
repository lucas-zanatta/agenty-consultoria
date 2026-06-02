import logging
import sys
from pathlib import Path

import stripe
from fastapi import APIRouter, Header, HTTPException, Request

sys.path.insert(0, str(Path(__file__).parent))
import config
import db
import notifier

log = logging.getLogger("agenty.webhook")

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
        _handle_checkout_completed(event["data"]["object"])

    elif event["type"] == "customer.subscription.deleted":
        _handle_subscription_deleted(event["data"]["object"])

    return {"received": True}


def _handle_checkout_completed(session: dict):
    customer_id   = session.get("customer", "")
    customer_name  = session.get("customer_details", {}).get("name", "")
    customer_email = session.get("customer_details", {}).get("email", "")
    subscription_id = session.get("subscription", "")

    if not customer_email:
        log.warning("checkout.session.completed sem e-mail — ignorado")
        return

    log.info(f"Novo cliente via Stripe: {customer_email}")

    client = db.create_client_record(
        email=customer_email,
        name=customer_name,
        stripe_customer_id=customer_id,
        stripe_subscription_id=subscription_id,
    )

    notifier.send_onboarding_email(
        email=customer_email,
        name=customer_name,
        onboarding_token=client["onboarding_token"],
    )


def _handle_subscription_deleted(subscription: dict):
    customer_id = subscription.get("customer", "")
    if not customer_id:
        return

    from supabase import create_client as sb_create
    _sb = sb_create(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
    result = _sb.table("clients").select("id").eq("stripe_customer_id", customer_id).execute()

    if result.data:
        client_id = result.data[0]["id"]
        db.suspend_client(client_id)
        log.info(f"Cliente suspenso (assinatura cancelada): {customer_id}")
