import os
from pathlib import Path

_env = Path(__file__).parent.parent / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL         = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# ── Stripe ────────────────────────────────────────────────────────────────────
STRIPE_SECRET_KEY      = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET  = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_ID        = os.getenv("STRIPE_PRICE_ID", "")   # price_xxx do plano R$49,90/mês

# ── Google OAuth — conta Agenty (único app para todos os clientes) ─────────────
# Criado em console.cloud.google.com — Agenty é o publisher OAuth
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# ── SMTP (Gmail da Agenty — envia e-mails para todos os clientes) ─────────────
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# ── Anthropic ─────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ── Servidor ──────────────────────────────────────────────────────────────────
APP_BASE_URL          = os.getenv("APP_BASE_URL", "http://localhost:8000")
PORT                  = int(os.getenv("PORT", "8000"))
CHECK_INTERVAL_HOURS  = int(os.getenv("CHECK_INTERVAL_HOURS", "2"))
