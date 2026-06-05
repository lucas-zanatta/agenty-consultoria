import asyncio
import logging
import sys
import threading
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

sys.path.insert(0, str(Path(__file__).parent))
import claude_client
import config
import db
import notifier
import reviewer
from gmb_client import GMBClient
from onboarding import router as onboarding_router
from stripe_webhook import router as stripe_router
from webhook import router as webhook_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("agenty.main")

scheduler = AsyncIOScheduler()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "templates")
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        reviewer.run_all_clients,
        trigger="interval",
        hours=config.CHECK_INTERVAL_HOURS,
        id="review_cycle",
        max_instances=1,
    )
    scheduler.start()
    log.info(f"Scheduler iniciado — ciclo a cada {config.CHECK_INTERVAL_HOURS}h")

    threading.Thread(target=reviewer.run_all_clients, daemon=True).start()

    yield
    scheduler.shutdown()


app = FastAPI(title="Agenty — Gestor de Reputacao", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent.parent / "static")), name="static")
app.include_router(onboarding_router)
app.include_router(stripe_router)
app.include_router(webhook_router)


@app.get("/approve/{token}", response_class=HTMLResponse)
async def approve(request: Request, token: str):
    review = db.get_review_by_approval_token(token)
    if not review:
        return templates.TemplateResponse(
            request, "approve_result.html",
            context={"success": False, "reason": "invalid"},
            status_code=404,
        )

    client = db.get_client_by_id(review["client_id"])
    if not client:
        return templates.TemplateResponse(
            request, "approve_result.html",
            context={"success": False, "reason": "invalid"},
            status_code=404,
        )

    review_name = f"{client['google_location_name']}/reviews/{review['review_id']}"
    gmb         = GMBClient(refresh_token=client["google_refresh_token"])
    success     = await asyncio.get_event_loop().run_in_executor(
        None, gmb.post_reply, review_name, review["draft_response"]
    )

    if success:
        db.set_replied(client["id"], review["review_id"], review["draft_response"])
        return templates.TemplateResponse(
            request, "approve_result.html",
            context={"success": True, "client": client},
        )

    return templates.TemplateResponse(
        request, "approve_result.html",
        context={"success": False, "reason": "error"},
        status_code=500,
    )


@app.get("/revise/{token}", response_class=HTMLResponse)
async def revise_form(request: Request, token: str):
    review = db.get_review_by_approval_token(token)
    if not review:
        return templates.TemplateResponse(
            request, "approve_result.html",
            context={"success": False, "reason": "invalid"}, status_code=404,
        )
    return templates.TemplateResponse(
        request, "revise_form.html",
        context={"token": token, "draft": review["draft_response"]},
    )


@app.post("/revise/{token}", response_class=HTMLResponse)
async def revise_submit(request: Request, token: str, feedback: str = Form(...)):
    review = db.get_review_by_approval_token(token)
    if not review:
        return templates.TemplateResponse(
            request, "approve_result.html",
            context={"success": False, "reason": "invalid"}, status_code=404,
        )

    client = db.get_client_by_id(review["client_id"])
    if not client:
        return templates.TemplateResponse(
            request, "approve_result.html",
            context={"success": False, "reason": "invalid"}, status_code=404,
        )

    new_draft = claude_client.revise_response(
        business_name=client.get("business_name", ""),
        business_type=client.get("business_type", ""),
        business_city=client.get("business_city", "Curitiba"),
        tone=client.get("tone", "proximo_descontraido"),
        rating=review["rating"],
        author=review.get("author", ""),
        review_text=review.get("text", ""),
        current_draft=review["draft_response"],
        feedback=feedback,
    )

    # Salva novo rascunho (mantém o mesmo token)
    db.update_draft(review["review_id"], review["client_id"], new_draft)

    # Reenvia e-mail com nova versão para aprovação
    updated_review = {**review, "draft_response": new_draft}
    notifier.send_approval_email(client, updated_review, new_draft, token)

    return templates.TemplateResponse(
        request, "revise_sent.html",
        context={"draft": new_draft},
    )


@app.get("/custom/{token}", response_class=HTMLResponse)
async def custom_form(request: Request, token: str):
    review = db.get_review_by_approval_token(token)
    if not review:
        return templates.TemplateResponse(
            request, "approve_result.html",
            context={"success": False, "reason": "invalid"}, status_code=404,
        )
    return templates.TemplateResponse(
        request, "custom_form.html",
        context={"token": token, "review": review},
    )


@app.post("/custom/{token}", response_class=HTMLResponse)
async def custom_submit(request: Request, token: str, response_text: str = Form(...)):
    review = db.get_review_by_approval_token(token)
    if not review:
        return templates.TemplateResponse(
            request, "approve_result.html",
            context={"success": False, "reason": "invalid"}, status_code=404,
        )

    client = db.get_client_by_id(review["client_id"])
    if not client:
        return templates.TemplateResponse(
            request, "approve_result.html",
            context={"success": False, "reason": "invalid"}, status_code=404,
        )

    review_name = f"{client['google_location_name']}/reviews/{review['review_id']}"
    gmb = GMBClient(refresh_token=client["google_refresh_token"])
    success = await asyncio.get_event_loop().run_in_executor(
        None, gmb.post_reply, review_name, response_text.strip()
    )

    if success:
        db.set_replied(client["id"], review["review_id"], response_text.strip())
        return templates.TemplateResponse(
            request, "approve_result.html",
            context={"success": True, "client": client},
        )

    return templates.TemplateResponse(
        request, "approve_result.html",
        context={"success": False, "reason": "error"}, status_code=500,
    )


@app.get("/health")
async def health():
    clients = db.get_active_clients()
    return {"status": "ok", "active_clients": len(clients)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=False)
