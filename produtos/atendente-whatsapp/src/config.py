import os
from pathlib import Path

_env = Path(__file__).parent.parent / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

ANTHROPIC_API_KEY    = os.getenv("ANTHROPIC_API_KEY", "")
VOYAGE_API_KEY       = os.getenv("VOYAGE_API_KEY", "")

SUPABASE_URL         = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

STRIPE_SECRET_KEY    = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

WA_VERIFY_TOKEN      = os.getenv("WA_VERIFY_TOKEN", "agenty-verify-token")

SMTP_HOST            = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT            = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER            = os.getenv("SMTP_USER", "")
SMTP_PASSWORD        = os.getenv("SMTP_PASSWORD", "")

APP_BASE_URL         = os.getenv("APP_BASE_URL", "http://localhost:8000")
PORT                 = int(os.getenv("PORT", "8000"))
