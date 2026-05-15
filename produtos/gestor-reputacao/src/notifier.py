import logging
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config

log = logging.getLogger("agenty.notifier")

_STARS = {1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐", 4: "⭐⭐⭐⭐", 5: "⭐⭐⭐⭐⭐"}

_BORDER_COLOR = {1: "#ef4444", 2: "#ef4444", 3: "#f59e0b", 4: "#10b981", 5: "#10b981"}


def send_approval_email(review: dict, draft: str, token: str):
    rating      = review.get("rating", 0)
    author      = review.get("author") or "Anônimo"
    review_text = review.get("text") or "<em>Sem texto</em>"
    stars       = _STARS.get(rating, str(rating))
    border      = _BORDER_COLOR.get(rating, "#94a3b8")
    urgency     = " — URGENTE" if rating <= 2 else ""
    approve_url = f"{config.APP_BASE_URL}/approve/{token}"

    subject = f"[Agenty] Avaliacao {stars} aguarda aprovacao{urgency} — {config.BUSINESS_NAME}"

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:32px 16px">
<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)">

  <!-- Header -->
  <tr><td style="background:#080812;padding:24px 32px">
    <p style="margin:0;color:#7c5cfc;font-size:22px;font-weight:bold">Agenty</p>
    <p style="margin:4px 0 0;color:#64748b;font-size:13px">Gestor de Reputacao Automatico</p>
  </td></tr>

  <!-- Body -->
  <tr><td style="padding:32px">
    <h2 style="margin:0 0 20px;color:#0f172a;font-size:18px">Nova avaliacao recebida em {config.BUSINESS_NAME}</h2>

    <!-- Review card -->
    <div style="border-left:4px solid {border};background:#f8fafc;padding:16px 20px;border-radius:6px;margin-bottom:24px">
      <p style="margin:0 0 6px;font-size:14px;color:#64748b">
        <strong style="color:#0f172a">{stars} {rating}/5</strong> &nbsp;·&nbsp; {author}
      </p>
      <p style="margin:0;color:#334155;font-size:15px;line-height:1.6">{review_text}</p>
    </div>

    <!-- Draft -->
    <p style="margin:0 0 10px;font-weight:bold;color:#0f172a">Resposta sugerida pela Agenty:</p>
    <div style="background:#f0f4ff;border:1px solid #c7d2fe;padding:16px 20px;border-radius:6px;margin-bottom:28px">
      <p style="margin:0;color:#1e293b;font-style:italic;line-height:1.7">"{draft}"</p>
    </div>

    <!-- CTA -->
    <div style="text-align:center;margin-bottom:28px">
      <a href="{approve_url}"
         style="display:inline-block;background:#7c5cfc;color:#ffffff;padding:14px 36px;border-radius:8px;text-decoration:none;font-weight:bold;font-size:16px;letter-spacing:.3px">
        Aprovar e publicar no Google
      </a>
    </div>

    <p style="margin:0;color:#94a3b8;font-size:13px;line-height:1.6">
      Quer ajustar o texto antes de publicar? Responda este e-mail com sua versao.<br>
      Este link expira em 72 horas.
    </p>
  </td></tr>

  <!-- Footer -->
  <tr><td style="background:#f8fafc;padding:16px 32px;border-top:1px solid #e2e8f0;text-align:center">
    <p style="margin:0;color:#94a3b8;font-size:12px">
      Agenty — Sua empresa fatura mais com IA &nbsp;·&nbsp;
      <a href="https://agenty.com.br" style="color:#7c5cfc;text-decoration:none">agenty.com.br</a>
    </p>
  </td></tr>

</table>
</td></tr></table>
</body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Agenty <{config.SMTP_USER}>"
    msg["To"]      = config.APPROVAL_EMAIL
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_USER, config.APPROVAL_EMAIL, msg.as_string())
        log.info(f"E-mail de aprovacao enviado para {config.APPROVAL_EMAIL}")
    except Exception as e:
        log.error(f"Falha ao enviar e-mail: {e}")
