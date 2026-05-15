import logging
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config
import db
import claude_client
import notifier
from gmb_client import GMBClient

log = logging.getLogger("agenty.reviewer")

_gmb = GMBClient()


def run_cycle():
    log.info("Iniciando ciclo de verificacao de avaliacoes...")

    try:
        raw_reviews = _gmb.list_unanswered_reviews()
    except Exception as e:
        log.error(f"Erro ao buscar avaliacoes na API do Google: {e}")
        return

    log.info(f"{len(raw_reviews)} avaliacoes sem resposta encontradas")

    # Registra no banco qualquer avaliação ainda não vista
    for raw in raw_reviews:
        review = GMBClient.parse_review(raw)
        db.upsert_review(review)

    # Processa as pendentes
    pending = db.get_pending()
    log.info(f"{len(pending)} avaliacoes pendentes para processar")

    for review in pending:
        _process(review, raw_reviews)
        time.sleep(7)  # max ~8 replies/min — rate limit da GMB API


def _process(review: dict, raw_reviews: list):
    review_id = review["review_id"]
    rating    = review["rating"]
    author    = review.get("author") or "Cliente"
    text      = review.get("text") or ""

    # Monta o nome completo da avaliação para a API
    raw = next((r for r in raw_reviews if r.get("reviewId") == review_id), {})
    review_name = raw.get("name") or f"{config.GOOGLE_LOCATION_NAME}/reviews/{review_id}"

    log.info(f"Processando avaliacao de {author} ({rating} estrelas)")

    try:
        draft = claude_client.generate_response(rating, author, text)
    except Exception as e:
        log.error(f"Erro ao gerar resposta para {review_id}: {e}")
        return

    if rating >= config.AUTO_REPLY_MIN_RATING:
        success = _gmb.post_reply(review_name, draft)
        if success:
            db.set_replied(review_id, draft)
            log.info(f"Auto-respondido: {author} ({rating} estrelas)")
    else:
        token = db.set_draft(review_id, draft)
        notifier.send_approval_email(review, draft, token)
        log.info(f"Rascunho enviado para aprovacao: {author} ({rating} estrelas)")
