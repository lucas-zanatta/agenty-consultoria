import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

sys.path.insert(0, str(Path(__file__).parent))
import config
import db
import reviewer
from gmb_client import GMBClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("agenty.main")

scheduler = AsyncIOScheduler()

_PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Agenty</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:#080812;color:#e2e8f0;font-family:Arial,sans-serif;
          display:flex;align-items:center;justify-content:center;min-height:100vh;padding:16px}}
    .card{{background:#0f0f23;border:1px solid #1e1e3f;border-radius:12px;
           padding:40px 48px;max-width:480px;width:100%;text-align:center}}
    .logo{{color:#7c5cfc;font-size:24px;font-weight:bold;margin-bottom:24px}}
    .badge{{display:inline-block;padding:10px 24px;border-radius:20px;
            font-weight:bold;font-size:16px;margin-bottom:20px}}
    .badge.ok{{background:#10b981;color:#fff}}
    .badge.err{{background:#ef4444;color:#fff}}
    .badge.warn{{background:#f59e0b;color:#fff}}
    p{{color:#94a3b8;line-height:1.6;margin-bottom:12px}}
    a{{color:#7c5cfc;text-decoration:none}}
  </style>
</head>
<body><div class="card">
  <div class="logo">Agenty</div>
  <div class="badge {css}">{icon} {title}</div>
  <p>{detail}</p>
  <p style="font-size:13px"><a href="https://agenty.com.br">agenty.com.br</a></p>
</div></body></html>"""


def _page(css: str, icon: str, title: str, detail: str) -> str:
    return _PAGE.format(css=css, icon=icon, title=title, detail=detail)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    loop = asyncio.get_event_loop()

    scheduler.add_job(
        lambda: loop.run_in_executor(None, reviewer.run_cycle),
        trigger="interval",
        hours=config.CHECK_INTERVAL_HOURS,
        id="review_cycle",
        max_instances=1,
    )
    scheduler.start()
    log.info(f"Scheduler iniciado — ciclo a cada {config.CHECK_INTERVAL_HOURS}h")

    # Roda imediatamente na inicialização
    loop.run_in_executor(None, reviewer.run_cycle)

    yield
    scheduler.shutdown()


app = FastAPI(title="Agenty — Gestor de Reputacao", lifespan=lifespan)


@app.get("/approve/{token}", response_class=HTMLResponse)
async def approve(token: str):
    review = db.get_by_token(token)
    if not review:
        return HTMLResponse(_page(
            "warn", "⚠️", "Link inválido ou expirado",
            "Este link já foi utilizado ou não existe. Nenhuma ação foi realizada."
        ), status_code=404)

    gmb = GMBClient()
    review_name = f"{config.GOOGLE_LOCATION_NAME}/reviews/{review['review_id']}"

    success = await asyncio.get_event_loop().run_in_executor(
        None, gmb.post_reply, review_name, review["draft_response"]
    )

    if success:
        db.set_replied(review["review_id"], review["draft_response"])
        return HTMLResponse(_page(
            "ok", "✅", "Resposta publicada!",
            "Sua resposta foi publicada com sucesso no Google. "
            "Ela aparecerá publicamente em alguns instantes."
        ))

    return HTMLResponse(_page(
        "err", "❌", "Erro ao publicar",
        "Não foi possível publicar a resposta. "
        "Entre em contato com a Agenty para resolver."
    ), status_code=500)


@app.get("/health")
async def health():
    return {"status": "ok", "business": config.BUSINESS_NAME}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=False)
