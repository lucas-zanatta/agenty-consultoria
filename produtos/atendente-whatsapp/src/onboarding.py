import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

sys.path.insert(0, str(Path(__file__).parent))
import config
import db
import rag

log = logging.getLogger("agenty.onboarding")

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


# ── Passo 1: Questionário do negócio ─────────────────────────────────────────

@router.get("/onboarding/{token}", response_class=HTMLResponse)
async def onboarding_form(request: Request, token: str):
    client = db.get_client_by_onboarding_token(token)
    if not client:
        return HTMLResponse("<h2>Link inválido ou expirado.</h2>", status_code=404)
    if client["status"] in ("active", "pending_meta_setup"):
        return templates.TemplateResponse(
            request, "onboarding_done.html", context={"client": client}
        )
    return templates.TemplateResponse(
        request, "onboarding_step1.html", context={"token": token, "client": client}
    )


@router.post("/onboarding/{token}/setup")
async def onboarding_setup(
    token: str,
    biz_name:             str = Form(...),
    biz_type:             str = Form(...),
    biz_city:             str = Form("Curitiba"),
    biz_services:         str = Form(""),
    biz_prices:           str = Form(""),
    biz_address:          str = Form(""),
    biz_payment_methods:  str = Form(""),
    biz_cancellation:     str = Form(""),
    biz_differentials:    str = Form(""),
    biz_extra:            str = Form(""),
    business_hours_start: int = Form(8),
    business_hours_end:   int = Form(18),
    out_of_hours_message: str = Form(""),
    handover_phone:       str = Form(""),
    cal_api_key:          str = Form(""),
    cal_event_type_id:    str = Form(""),
):
    client = db.get_client_by_onboarding_token(token)
    if not client:
        return HTMLResponse("<h2>Link inválido ou expirado.</h2>", status_code=404)

    db.update_client(
        client["id"],
        biz_name=biz_name,
        biz_type=biz_type,
        biz_city=biz_city,
        biz_services=biz_services,
        biz_prices=biz_prices,
        biz_address=biz_address,
        biz_payment_methods=biz_payment_methods,
        biz_cancellation=biz_cancellation,
        biz_differentials=biz_differentials,
        biz_extra=biz_extra,
        business_hours_start=business_hours_start,
        business_hours_end=business_hours_end,
        out_of_hours_message=out_of_hours_message,
        handover_phone=handover_phone,
        cal_api_key=cal_api_key or None,
        cal_event_type_id=cal_event_type_id or None,
    )
    return RedirectResponse(f"/onboarding/{token}/documents", status_code=303)


# ── Passo 2: Upload de documentos (opcional) ──────────────────────────────────

@router.get("/onboarding/{token}/documents", response_class=HTMLResponse)
async def onboarding_documents(request: Request, token: str):
    client = db.get_client_by_onboarding_token(token)
    if not client:
        return HTMLResponse("<h2>Link inválido ou expirado.</h2>", status_code=404)
    return templates.TemplateResponse(
        request, "onboarding_step2.html", context={"token": token, "client": client}
    )


@router.post("/onboarding/{token}/upload")
async def onboarding_upload(
    request: Request,
    token: str,
    files: list[UploadFile] = File(default=[]),
):
    client = db.get_client_by_onboarding_token(token)
    if not client:
        return HTMLResponse("<h2>Link inválido ou expirado.</h2>", status_code=404)

    errors = []
    total_chunks = 0

    for upload in files:
        if not upload.filename or not upload.filename.lower().endswith(".pdf"):
            errors.append(f"'{upload.filename}' não é um PDF.")
            continue
        file_bytes = await upload.read()
        if len(file_bytes) > 10 * 1024 * 1024:  # 10 MB
            errors.append(f"'{upload.filename}' excede 10 MB.")
            continue

        try:
            n = rag.process_pdf(
                client_id=client["id"],
                filename=upload.filename,
                file_bytes=file_bytes,
            )
            total_chunks += n
            log.info(f"PDF '{upload.filename}' processado: {n} chunks")
        except Exception as e:
            log.error(f"Erro ao processar '{upload.filename}': {e}")
            errors.append(f"Erro ao processar '{upload.filename}'.")

    # Avança para conclusão
    db.update_client(client["id"], status="pending_meta_setup")
    client = db.get_client_by_id(client["id"])

    return templates.TemplateResponse(
        request, "onboarding_done.html",
        context={"client": client, "chunks": total_chunks, "errors": errors},
    )


@router.post("/onboarding/{token}/skip-documents")
async def onboarding_skip_documents(request: Request, token: str):
    client = db.get_client_by_onboarding_token(token)
    if not client:
        return HTMLResponse("<h2>Link inválido ou expirado.</h2>", status_code=404)
    db.update_client(client["id"], status="pending_meta_setup")
    client = db.get_client_by_id(client["id"])
    return templates.TemplateResponse(
        request, "onboarding_done.html", context={"client": client, "chunks": 0, "errors": []}
    )
