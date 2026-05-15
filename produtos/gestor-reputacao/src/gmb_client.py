import logging
import sys
from pathlib import Path

import httpx
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

sys.path.insert(0, str(Path(__file__).parent))
import config
from mock_reviews import MOCK_REVIEWS

log = logging.getLogger("agenty.gmb")

_REVIEWS_BASE = "https://mybusiness.googleapis.com/v4"
_SCOPES = ["https://www.googleapis.com/auth/business.manage"]

# Mapeamento da API do Google para inteiros
_STAR_MAP = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}


class GMBClient:

    def __init__(self):
        self._creds = Credentials(
            token=None,
            refresh_token=config.GOOGLE_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=config.GOOGLE_CLIENT_ID,
            client_secret=config.GOOGLE_CLIENT_SECRET,
            scopes=_SCOPES,
        )

    def _headers(self) -> dict:
        if not self._creds.valid:
            self._creds.refresh(Request())
        return {
            "Authorization": f"Bearer {self._creds.token}",
            "Content-Type": "application/json",
        }

    def list_unanswered_reviews(self) -> list[dict]:
        """Retorna avaliações sem resposta do local configurado."""
        if config.MOCK_MODE:
            log.info("[MOCK] Retornando avaliacoes fictícias")
            return MOCK_REVIEWS

        url = f"{_REVIEWS_BASE}/{config.GOOGLE_LOCATION_NAME}/reviews"
        reviews = []
        page_token = None

        with httpx.Client(timeout=30) as client:
            while True:
                params = {"pageSize": 50}
                if page_token:
                    params["pageToken"] = page_token

                resp = client.get(url, headers=self._headers(), params=params)
                resp.raise_for_status()
                data = resp.json()

                for r in data.get("reviews", []):
                    if "reviewReply" not in r:
                        reviews.append(r)

                page_token = data.get("nextPageToken")
                if not page_token:
                    break

        return reviews

    def post_reply(self, review_name: str, text: str) -> bool:
        """Publica uma resposta para uma avaliação. Retorna True se bem-sucedido."""
        if config.MOCK_MODE:
            log.info(f"[MOCK] Resposta publicada (simulada): {review_name}")
            return True

        url = f"{_REVIEWS_BASE}/{review_name}/reply"
        with httpx.Client(timeout=30) as client:
            resp = client.put(url, headers=self._headers(), json={"comment": text})

        if resp.status_code in (200, 201):
            log.info(f"Resposta publicada: {review_name}")
            return True

        log.warning(f"Erro ao publicar ({resp.status_code}): {resp.text[:200]}")
        return False

    @staticmethod
    def parse_review(raw: dict) -> dict:
        """Converte o formato bruto da API para o formato interno."""
        return {
            "review_id":     raw["reviewId"],
            "location_name": config.GOOGLE_LOCATION_NAME,
            "rating":        _STAR_MAP.get(raw.get("starRating", ""), 0),
            "author":        raw.get("reviewer", {}).get("displayName", ""),
            "text":          raw.get("comment", ""),
            "created_at":    raw.get("createTime", ""),
        }
