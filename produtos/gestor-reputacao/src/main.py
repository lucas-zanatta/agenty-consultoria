import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

sys.path.insert(0, str(Path(__file__).parent))
import config
import db
import reviewer
from gmb_client import GMBClient
from onboarding import router as onboarding_router
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
        lambda: asyncio.get_event_loop().run_in_executor(None, reviewer.run_all_clients),
        trigger="interval",
        hours=config.CHECK_INTERVAL_HOURS,
        id="review_cycle",
        max_instances=1,
    )
    scheduler.start()
    log.info(f"Scheduler iniciado — ciclo a cada {config.CHECK_INTERVAL_HOURS}h")

    asyncio.get_event_loop().run_in_executor(None, reviewer.run_all_clients)

    yield
    scheduler.shutdown()


app = FastAPI(title="Agenty — Gestor de Reputacao", lifespan=lifespan)
app.include_router(onboarding_router)
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


@app.get("/health")
async def health():
    clients = db.get_active_clients()
    return {"status": "ok", "active_clients": len(clients)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=False)
