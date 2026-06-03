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
_BORDER = {1: "#ef4444", 2: "#ef4444", 3: "#f59e0b", 4: "#10b981", 5: "#10b981"}


def send_approval_email(client: dict, review: dict, draft: str, token: str):
    rating      = review.get("rating", 0)
    author      = review.get("author") or "Anônimo"
    review_text = review.get("text") or "<em>Sem texto</em>"
    stars       = _STARS.get(rating, str(rating))
    border      = _BORDER.get(rating, "#94a3b8")
    urgency     = " — URGENTE" if rating <= 2 else ""
    approve_url = f"{config.APP_BASE_URL}/approve/{token}"
    revise_url  = f"{config.APP_BASE_URL}/revise/{token}"
    custom_url  = f"{config.APP_BASE_URL}/custom/{token}"

    business_name  = client.get("business_name") or client["email"]
    approval_email = client.get("approval_email") or client["email"]

    subject = f"[Agenty] Avaliacao {stars} aguarda aprovacao{urgency} — {business_name}"

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:32px 16px">
<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)">

  <tr><td style="background:#080812;padding:24px 32px">
    <p style="margin:0;color:#c94a1f;font-size:22px;font-weight:bold">Agenty</p>
    <p style="margin:4px 0 0;color:#64748b;font-size:13px">Gestor de Reputacao Automatico</p>
  </td></tr>

  <tr><td style="padding:32px">
    <h2 style="margin:0 0 20px;color:#0f172a;font-size:18px">Nova avaliacao recebida em {business_name}</h2>

    <div style="border-left:4px solid {border};background:#f8fafc;padding:16px 20px;border-radius:6px;margin-bottom:24px">
      <p style="margin:0 0 6px;font-size:14px;color:#64748b">
        <strong style="color:#0f172a">{stars} {rating}/5</strong> &nbsp;·&nbsp; {author}
      </p>
      <p style="margin:0;color:#334155;font-size:15px;line-height:1.6">{review_text}</p>
    </div>

    <p style="margin:0 0 10px;font-weight:bold;color:#0f172a">Resposta sugerida pela Agenty:</p>
    <div style="background:#fff7f0;border:1px solid #f2b705;padding:16px 20px;border-radius:6px;margin-bottom:28px">
      <p style="margin:0;color:#1e293b;font-style:italic;line-height:1.7">"{draft}"</p>
    </div>

    <!-- 3 ações -->
    <div style="text-align:center;margin-bottom:16px">
      <a href="{approve_url}"
         style="display:inline-block;background:#c94a1f;color:#ffffff;padding:14px 36px;border-radius:8px;text-decoration:none;font-weight:bold;font-size:15px;letter-spacing:.3px">
        Aprovar e publicar no Google
      </a>
    </div>
    <div style="text-align:center;margin-bottom:16px">
      <a href="{revise_url}"
         style="display:inline-block;background:#f0f4ff;color:#1e293b;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:bold;font-size:14px;border:1px solid #c7d2fe">
        Pedir modificações à IA
      </a>
    </div>
    <div style="text-align:center;margin-bottom:28px">
      <a href="{custom_url}"
         style="display:inline-block;background:#f8fafc;color:#64748b;padding:12px 28px;border-radius:8px;text-decoration:none;font-size:14px;border:1px solid #e2e8f0">
        Escrever minha própria resposta
      </a>
    </div>

    <p style="margin:0;color:#94a3b8;font-size:12px;line-height:1.6;text-align:center">
      Este link expira em 72 horas.
    </p>
  </td></tr>

  <tr><td style="background:#f8fafc;padding:16px 32px;border-top:1px solid #e2e8f0;text-align:center">
    <p style="margin:0;color:#94a3b8;font-size:12px">
      Agenty — Sua empresa fatura mais com IA &nbsp;·&nbsp;
      <a href="https://agenty.com.br" style="color:#c94a1f;text-decoration:none">agenty.com.br</a>
    </p>
  </td></tr>

</table>
</td></tr></table>
</body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Agenty <{config.SMTP_USER}>"
    msg["To"]      = approval_email
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_USER, approval_email, msg.as_string())
        log.info(f"E-mail de aprovacao enviado para {approval_email}")
    except Exception as e:
        log.error(f"Falha ao enviar e-mail: {e}")


def send_onboarding_email(email: str, name: str, onboarding_token: str):
    """Envia o link de onboarding após o pagamento ser confirmado."""
    onboarding_url = f"{config.APP_BASE_URL}/onboarding/{onboarding_token}"
    first_name = name.split()[0] if name else "cliente"

    subject = f"[Agenty] Configure sua automacao em 5 minutos"

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:32px 16px">
<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)">

  <tr><td style="background:#080812;padding:24px 32px">
    <p style="margin:0;color:#c94a1f;font-size:22px;font-weight:bold">Agenty</p>
    <p style="margin:4px 0 0;color:#64748b;font-size:13px">Gestor de Reputacao Automatico</p>
  </td></tr>

  <tr><td style="padding:32px">
    <h2 style="margin:0 0 16px;color:#0f172a;font-size:22px">Olá, {first_name}!</h2>
    <p style="margin:0 0 16px;color:#334155;line-height:1.7;font-size:15px">
      Seu Gestor de Reputacao esta pronto para ser configurado. Leva menos de 5 minutos.
    </p>
    <p style="margin:0 0 24px;color:#334155;line-height:1.7;font-size:15px">
      Voce vai precisar de:
    </p>
    <ul style="margin:0 0 28px;padding-left:20px;color:#334155;line-height:2;font-size:15px">
      <li>Informacoes basicas sobre seu negocio</li>
      <li>Login com a conta Google do seu negocio (Google Meu Negocio)</li>
    </ul>

    <div style="text-align:center;margin-bottom:28px">
      <a href="{onboarding_url}"
         style="display:inline-block;background:#c94a1f;color:#ffffff;padding:16px 40px;border-radius:8px;text-decoration:none;font-weight:bold;font-size:16px;letter-spacing:.3px">
        Configurar minha automacao
      </a>
    </div>

    <p style="margin:0;color:#94a3b8;font-size:13px;line-height:1.6">
      Este link e unico para voce e expira em 7 dias.<br>
      Qualquer duvida, responda este e-mail.
    </p>
  </td></tr>

  <tr><td style="background:#f8fafc;padding:16px 32px;border-top:1px solid #e2e8f0;text-align:center">
    <p style="margin:0;color:#94a3b8;font-size:12px">
      Agenty — Sua empresa fatura mais com IA &nbsp;·&nbsp;
      <a href="https://agenty.com.br" style="color:#c94a1f;text-decoration:none">agenty.com.br</a>
    </p>
  </td></tr>

</table>
</td></tr></table>
</body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Agenty <{config.SMTP_USER}>"
    msg["To"]      = email
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_USER, email, msg.as_string())
        log.info(f"E-mail de onboarding enviado para {email}")
    except Exception as e:
        log.error(f"Falha ao enviar e-mail de onboarding: {e}")
