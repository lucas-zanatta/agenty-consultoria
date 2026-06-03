import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from supabase import create_client, Client

sys.path.insert(0, str(Path(__file__).parent))
import config

_sb: Client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)


# ── Clients ───────────────────────────────────────────────────────────────────

def create_client_record(
    email: str,
    name: str,
    stripe_customer_id: str = "",
    stripe_subscription_id: str = "",
) -> dict:
    result = _sb.table("clients").insert({
        "email": email,
        "name": name,
        "stripe_customer_id": stripe_customer_id,
        "stripe_subscription_id": stripe_subscription_id,
        "status": "pending_onboarding",
    }).execute()
    return result.data[0]


def get_client_by_onboarding_token(token: str) -> dict | None:
    result = _sb.table("clients").select("*").eq("onboarding_token", token).execute()
    return result.data[0] if result.data else None


def get_client_by_id(client_id: str) -> dict | None:
    result = _sb.table("clients").select("*").eq("id", client_id).execute()
    return result.data[0] if result.data else None


def get_active_clients() -> list[dict]:
    result = _sb.table("clients").select("*").eq("status", "active").execute()
    return result.data


def update_client(client_id: str, **fields) -> dict:
    result = _sb.table("clients").update(fields).eq("id", client_id).execute()
    return result.data[0]


def activate_client(client_id: str) -> dict:
    return update_client(
        client_id,
        status="active",
        activated_at=datetime.now(timezone.utc).isoformat(),
    )


def suspend_client(client_id: str) -> dict:
    return update_client(client_id, status="suspended")


# ── Reviews ───────────────────────────────────────────────────────────────────

def upsert_review(client_id: str, review: dict):
    _sb.table("reviews").upsert({
        "client_id":   client_id,
        "review_id":   review["review_id"],
        "rating":      review["rating"],
        "author":      review["author"],
        "text":        review["text"],
        "created_at":  review["created_at"],
        "status":      "pending",
    }, on_conflict="client_id,review_id", ignore_duplicates=True).execute()


def get_pending_reviews(client_id: str) -> list[dict]:
    result = (
        _sb.table("reviews")
        .select("*")
        .eq("client_id", client_id)
        .eq("status", "pending")
        .execute()
    )
    return result.data


def set_draft(client_id: str, review_id: str, draft: str) -> str:
    token = str(uuid.uuid4())
    _sb.table("reviews").update({
        "status":         "draft_sent",
        "draft_response": draft,
        "approval_token": token,
    }).eq("client_id", client_id).eq("review_id", review_id).execute()
    return token


def update_draft(review_id: str, client_id: str, new_draft: str):
    _sb.table("reviews").update({
        "draft_response": new_draft,
    }).eq("review_id", review_id).eq("client_id", client_id).execute()


def set_replied(client_id: str, review_id: str, response: str):
    _sb.table("reviews").update({
        "status":         "replied",
        "final_response": response,
        "processed_at":   datetime.now(timezone.utc).isoformat(),
    }).eq("client_id", client_id).eq("review_id", review_id).execute()


def get_review_by_approval_token(token: str) -> dict | None:
    result = (
        _sb.table("reviews")
        .select("*")
        .eq("approval_token", token)
        .eq("status", "draft_sent")
        .execute()
    )
    return result.data[0] if result.data else None
