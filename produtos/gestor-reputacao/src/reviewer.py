import logging
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import db
import claude_client
import notifier
from gmb_client import GMBClient
from mock_reviews import MOCK_REVIEWS

log = logging.getLogger("agenty.reviewer")


def run_all_clients():
    """Ponto de entrada do scheduler — itera sobre todos os clientes ativos."""
    clients = db.get_active_clients()
    log.info(f"Ciclo iniciado — {len(clients)} cliente(s) ativo(s)")

    for client in clients:
        try:
            _run_cycle(client)
        except Exception as e:
            log.error(f"Erro no ciclo do cliente {client['id']} ({client['business_name']}): {e}")


def _run_cycle(client: dict):
    client_id     = client["id"]
    business_name = client.get("business_name") or client["email"]
    mock_mode     = not client.get("google_refresh_token")

    log.info(f"[{business_name}] Verificando avaliacoes...")

    if mock_mode:
        log.info(f"[{business_name}] Sem credenciais Google — usando mock")
        raw_reviews = MOCK_REVIEWS
    else:
        try:
            gmb = GMBClient(refresh_token=client["google_refresh_token"])
            raw_reviews = gmb.list_unanswered_reviews(client["google_location_name"])
        except Exception as e:
            log.error(f"[{business_name}] Erro ao buscar avaliacoes: {e}")
            return

    log.info(f"[{business_name}] {len(raw_reviews)} avaliacao(oes) sem resposta")

    for raw in raw_reviews:
        review = GMBClient.parse_review(raw)
        db.upsert_review(client_id, review)

    pending = db.get_pending_reviews(client_id)
    log.info(f"[{business_name}] {len(pending)} pendente(s) para processar")

    for review in pending:
        _process(client, review, raw_reviews, mock_mode)
        time.sleep(7)  # rate limit GMB API: ~8 replies/min


def _process(client: dict, review: dict, raw_reviews: list, mock_mode: bool):
    client_id  = client["id"]
    review_id  = review["review_id"]
    rating     = review["rating"]
    author     = review.get("author") or "Cliente"
    text       = review.get("text") or ""
    min_rating = client.get("auto_reply_min_rating") or 4

    raw = next((r for r in raw_reviews if r.get("reviewId") == review_id), {})
    review_name = raw.get("name") or f"{client['google_location_name']}/reviews/{review_id}"

    business_name = client.get("business_name", "")
    log.info(f"[{business_name}] Processando: {author} ({rating} estrelas)")

    try:
        draft = claude_client.generate_response(
            business_name=business_name,
            business_type=client.get("business_type", ""),
            business_city=client.get("business_city", "Curitiba"),
            tone=client.get("tone", "proximo_descontraido"),
            rating=rating,
            author=author,
            review_text=text,
        )
    except Exception as e:
        log.error(f"[{business_name}] Erro ao gerar resposta para {review_id}: {e}")
        return

    if rating >= min_rating:
        if mock_mode:
            log.info(f"[{business_name}] [MOCK] Auto-respondido: {author}")
            db.set_replied(client_id, review_id, draft)
        else:
            gmb = GMBClient(refresh_token=client["google_refresh_token"])
            success = gmb.post_reply(review_name, draft)
            if success:
                db.set_replied(client_id, review_id, draft)
                log.info(f"[{business_name}] Auto-respondido: {author}")
    else:
        token = db.set_draft(client_id, review_id, draft)
        notifier.send_approval_email(client, review, draft, token)
        log.info(f"[{business_name}] Rascunho enviado para aprovacao: {author}")
