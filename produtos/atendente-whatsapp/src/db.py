import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from supabase import create_client, Client

sys.path.insert(0, str(Path(__file__).parent))
import config

_sb: Client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)


# ── wa_clients ────────────────────────────────────────────────────────────────

def create_client_record(email: str, name: str,
                         stripe_customer_id: str = "",
                         stripe_subscription_id: str = "") -> dict:
    result = _sb.table("wa_clients").insert({
        "email": email,
        "name": name,
        "stripe_customer_id": stripe_customer_id,
        "stripe_subscription_id": stripe_subscription_id,
        "status": "pending_onboarding",
    }).execute()
    return result.data[0]


def get_client_by_onboarding_token(token: str) -> dict | None:
    result = _sb.table("wa_clients").select("*").eq("onboarding_token", token).execute()
    return result.data[0] if result.data else None


def get_client_by_phone_number_id(phone_number_id: str) -> dict | None:
    result = _sb.table("wa_clients").select("*").eq("phone_number_id", phone_number_id).eq("status", "active").execute()
    return result.data[0] if result.data else None


def get_client_by_id(client_id: str) -> dict | None:
    result = _sb.table("wa_clients").select("*").eq("id", client_id).execute()
    return result.data[0] if result.data else None


def get_active_clients() -> list[dict]:
    result = _sb.table("wa_clients").select("*").eq("status", "active").execute()
    return result.data


def update_client(client_id: str, **fields) -> dict:
    result = _sb.table("wa_clients").update(fields).eq("id", client_id).execute()
    return result.data[0]


def activate_client(client_id: str) -> dict:
    return update_client(client_id, status="active",
                         activated_at=datetime.now(timezone.utc).isoformat())


def suspend_client(client_id: str) -> dict:
    return update_client(client_id, status="suspended")


# ── wa_conversations ──────────────────────────────────────────────────────────

def get_or_create_conversation(client_id: str, customer_phone: str) -> dict:
    result = (
        _sb.table("wa_conversations")
        .select("*")
        .eq("client_id", client_id)
        .eq("customer_phone", customer_phone)
        .execute()
    )
    if result.data:
        return result.data[0]

    result = _sb.table("wa_conversations").insert({
        "client_id":      client_id,
        "customer_phone": customer_phone,
        "status":         "active",
        "last_message_at": datetime.now(timezone.utc).isoformat(),
    }).execute()
    return result.data[0]


def increment_message_count(conversation_id: str) -> int:
    conv = _sb.table("wa_conversations").select("message_count").eq("id", conversation_id).execute()
    count = (conv.data[0]["message_count"] or 0) + 1
    _sb.table("wa_conversations").update({
        "message_count":   count,
        "last_message_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", conversation_id).execute()
    return count


def set_conversation_handed_over(conversation_id: str):
    _sb.table("wa_conversations").update({"status": "handed_over"}).eq("id", conversation_id).execute()


def save_lead(conversation_id: str, lead_data: dict):
    _sb.table("wa_conversations").update({
        "lead_captured": True,
        "lead_data":     lead_data,
    }).eq("id", conversation_id).execute()


def update_customer_name(conversation_id: str, name: str):
    _sb.table("wa_conversations").update({"customer_name": name}).eq("id", conversation_id).execute()


# ── wa_messages ───────────────────────────────────────────────────────────────

def save_message(conversation_id: str, role: str, content: str,
                 wa_message_id: str | None = None):
    payload = {"conversation_id": conversation_id, "role": role, "content": content}
    if wa_message_id:
        payload["wa_message_id"] = wa_message_id
    _sb.table("wa_messages").insert(payload).execute()


def is_duplicate_message(wa_message_id: str) -> bool:
    result = _sb.table("wa_messages").select("id").eq("wa_message_id", wa_message_id).execute()
    return bool(result.data)


def get_recent_messages(conversation_id: str, limit: int = 10) -> list[dict]:
    result = (
        _sb.table("wa_messages")
        .select("role, content")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    return result.data


# ── wa_documents (RAG) ────────────────────────────────────────────────────────

def save_document_chunks(client_id: str, filename: str,
                         storage_path: str, chunks: list[dict]):
    rows = [
        {
            "client_id":    client_id,
            "filename":     filename,
            "storage_path": storage_path,
            "chunk_index":  i,
            "content":      c["content"],
            "embedding":    c["embedding"],
        }
        for i, c in enumerate(chunks)
    ]
    _sb.table("wa_documents").insert(rows).execute()


def similarity_search(client_id: str, embedding: list[float], top_k: int = 3) -> list[str]:
    result = _sb.rpc("match_wa_documents", {
        "p_client_id":    client_id,
        "query_embedding": embedding,
        "match_count":    top_k,
    }).execute()
    return [r["content"] for r in result.data] if result.data else []


def delete_client_documents(client_id: str):
    _sb.table("wa_documents").delete().eq("client_id", client_id).execute()
