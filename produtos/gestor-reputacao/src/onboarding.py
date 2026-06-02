import logging
import sys
from pathlib import Path
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from google_auth_oauthlib.flow import Flow

sys.path.insert(0, str(Path(__file__).parent))
import config
import db
from gmb_client import list_accounts, list_locations

log = logging.getLogger("agenty.onboarding")

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "templates")
)

_SCOPES = ["https://www.googleapis.com/auth/business.manage"]

# onboarding_token → OAuth state para recuperar no callback
_pending_oauth: dict[str, str] = {}


def _build_flow() -> Flow:
    return Flow.from_client_config(
        {
            "web": {
                "client_id":                config.GOOGLE_CLIENT_ID,
                "client_secret":            config.GOOGLE_CLIENT_SECRET,
                "auth_uri":                 "https://accounts.google.com/o/oauth2/auth",
                "token_uri":                "https://oauth2.googleapis.com/token",
                "redirect_uris":            [f"{config.APP_BASE_URL}/oauth/callback"],
            }
        },
        scopes=_SCOPES,
        redirect_uri=f"{config.APP_BASE_URL}/oauth/callback",
    )


# ── Passo 1: formulário de informações do negócio ─────────────────────────────

@router.get("/onboarding/{token}", response_class=HTMLResponse)
async def onboarding_form(request: Request, token: str):
    client = db.get_client_by_onboarding_token(token)
    if not client:
        return HTMLResponse("<h2>Link inválido ou expirado.</h2>", status_code=404)
    if client["status"] == "active":
        return templates.TemplateResponse(
            "onboarding_done.html", {"request": request, "client": client}
        )
    return templates.TemplateResponse(
        "onboarding_step1.html", {"request": request, "token": token, "client": client}
    )


@router.post("/onboarding/{token}/setup")
async def onboarding_setup(
    token: str,
    business_name:         str = Form(...),
    business_type:         str = Form(...),
    business_city:         str = Form("Curitiba"),
    tone:                  str = Form("proximo_descontraido"),
    approval_email:        str = Form(...),
    auto_reply_min_rating: int = Form(4),
):
    client = db.get_client_by_onboarding_token(token)
    if not client:
        return HTMLResponse("<h2>Link inválido ou expirado.</h2>", status_code=404)

    db.update_client(
        client["id"],
        business_name=business_name,
        business_type=business_type,
        business_city=business_city,
        tone=tone,
        approval_email=approval_email,
        auto_reply_min_rating=auto_reply_min_rating,
    )
    return RedirectResponse(
        f"/onboarding/{token}/connect", status_code=303
    )


# ── Passo 2: conectar Google Meu Negócio via OAuth ───────────────────────────

@router.get("/onboarding/{token}/connect", response_class=HTMLResponse)
async def onboarding_connect(request: Request, token: str):
    client = db.get_client_by_onboarding_token(token)
    if not client:
        return HTMLResponse("<h2>Link inválido ou expirado.</h2>", status_code=404)
    return templates.TemplateResponse(
        "onboarding_step2.html", {"request": request, "token": token, "client": client}
    )


@router.get("/onboarding/{token}/google-auth")
async def onboarding_google_auth(token: str):
    """Inicia o fluxo OAuth com o Google."""
    client = db.get_client_by_onboarding_token(token)
    if not client:
        return HTMLResponse("<h2>Link inválido ou expirado.</h2>", status_code=404)

    flow = _build_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=token,  # token de onboarding como state para recuperar no callback
    )
    _pending_oauth[state] = token
    return RedirectResponse(auth_url)


# ── Callback OAuth ────────────────────────────────────────────────────────────

@router.get("/oauth/callback", response_class=HTMLResponse)
async def oauth_callback(request: Request, code: str, state: str):
    token = _pending_oauth.pop(state, state)  # fallback: state é o próprio token

    client = db.get_client_by_onboarding_token(token)
    if not client:
        return HTMLResponse("<h2>Link inválido ou expirado.</h2>", status_code=404)

    flow = _build_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials

    # Salva o refresh_token no banco
    db.update_client(client["id"], google_refresh_token=creds.refresh_token)

    # Busca contas e locais do GMB com o access_token recém-obtido
    try:
        accounts  = list_accounts(creds.token)
        locations = []

        if len(accounts) == 1:
            acc = accounts[0]
            db.update_client(client["id"], google_account_name=acc["name"])
            locs = list_locations(creds.token, acc["name"])

            if len(locs) == 1:
                # Único local — ativa direto
                loc     = locs[0]
                loc_v4  = f"{acc['name']}/{loc['name']}"
                db.update_client(client["id"], google_location_name=loc_v4)
                db.activate_client(client["id"])
                client = db.get_client_by_id(client["id"])
                return templates.TemplateResponse(
                    "onboarding_done.html", {"request": request, "client": client}
                )

            locations = [(acc["name"], loc) for loc in locs]
        else:
            # Múltiplas contas — mostra seletor
            for acc in accounts:
                locs = list_locations(creds.token, acc["name"])
                for loc in locs:
                    locations.append((acc["name"], loc))

    except Exception as e:
        log.error(f"Erro ao buscar contas GMB: {e}")
        return HTMLResponse(
            "<h2>Erro ao acessar o Google Meu Negócio.</h2>"
            "<p>Certifique-se de que sua conta tem um perfil verificado e tente novamente.</p>",
            status_code=500,
        )

    return templates.TemplateResponse(
        "onboarding_select_location.html",
        {"request": request, "token": token, "locations": locations},
    )


@router.post("/onboarding/{token}/location")
async def onboarding_select_location(
    request: Request,
    token: str,
    account_name: str  = Form(...),
    location_name: str = Form(...),
):
    client = db.get_client_by_onboarding_token(token)
    if not client:
        return HTMLResponse("<h2>Link inválido ou expirado.</h2>", status_code=404)

    loc_v4 = f"{account_name}/{location_name}"
    db.update_client(
        client["id"],
        google_account_name=account_name,
        google_location_name=loc_v4,
    )
    db.activate_client(client["id"])
    client = db.get_client_by_id(client["id"])

    return templates.TemplateResponse(
        "onboarding_done.html", {"request": request, "client": client}
    )
