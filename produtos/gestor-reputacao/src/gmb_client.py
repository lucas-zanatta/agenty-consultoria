import logging

import httpx
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import config

log = logging.getLogger("agenty.gmb")

_REVIEWS_BASE = "https://mybusiness.googleapis.com/v4"
_SCOPES = ["https://www.googleapis.com/auth/business.manage"]
_STAR_MAP = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}


class GMBClient:

    def __init__(self, refresh_token: str):
        self._creds = Credentials(
            token=None,
            refresh_token=refresh_token,
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

    def list_unanswered_reviews(self, location_name: str) -> list[dict]:
        url = f"{_REVIEWS_BASE}/{location_name}/reviews"
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
        return {
            "review_id":  raw["reviewId"],
            "rating":     _STAR_MAP.get(raw.get("starRating", ""), 0),
            "author":     raw.get("reviewer", {}).get("displayName", ""),
            "text":       raw.get("comment", ""),
            "created_at": raw.get("createTime", ""),
        }


def list_accounts(access_token: str) -> list[dict]:
    """Lista contas do Google Business Profile — usado no onboarding OAuth."""
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = httpx.get(
        "https://mybusinessaccountmanagement.googleapis.com/v1/accounts",
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get("accounts", [])


def list_locations(access_token: str, account_name: str) -> list[dict]:
    """Lista locais de uma conta — usado no onboarding OAuth."""
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = httpx.get(
        f"https://mybusinessbusinessinformation.googleapis.com/v1/{account_name}/locations",
        headers=headers,
        params={"readMask": "name,title"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get("locations", [])
