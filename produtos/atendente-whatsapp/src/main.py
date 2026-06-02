import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

sys.path.insert(0, str(Path(__file__).parent))
import config
import db
from onboarding import router as onboarding_router
from stripe_webhook import router as stripe_router
from webhook import router as wa_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("agenty.main")

templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Zinvo iniciado")
    yield
    log.info("Zinvo encerrado")


app = FastAPI(title="Zinvo — Atendente WhatsApp Inteligente", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent.parent / "static")), name="static")
app.include_router(wa_router)
app.include_router(stripe_router)
app.include_router(onboarding_router)


@app.get("/health")
async def health():
    clients = db.get_active_clients()
    return {"status": "ok", "active_clients": len(clients)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=False)
