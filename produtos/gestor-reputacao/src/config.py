import os
from pathlib import Path

_env = Path(__file__).parent.parent / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

ANTHROPIC_API_KEY    = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN", "")
GOOGLE_ACCOUNT_NAME  = os.getenv("GOOGLE_ACCOUNT_NAME", "")   # ex: accounts/123456789
GOOGLE_LOCATION_NAME = os.getenv("GOOGLE_LOCATION_NAME", "")  # ex: accounts/123456789/locations/987654321

BUSINESS_NAME        = os.getenv("BUSINESS_NAME", "")
BUSINESS_TYPE        = os.getenv("BUSINESS_TYPE", "")
BUSINESS_CITY        = os.getenv("BUSINESS_CITY", "Curitiba")
BUSINESS_TONE        = os.getenv("BUSINESS_TONE", "proximo_descontraido")
# Tons disponíveis: profissional_cordial | proximo_descontraido | formal

APPROVAL_EMAIL       = os.getenv("APPROVAL_EMAIL", "")
SMTP_HOST            = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT            = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER            = os.getenv("SMTP_USER", "")
SMTP_PASSWORD        = os.getenv("SMTP_PASSWORD", "")  # Senha de app do Gmail

APP_BASE_URL         = os.getenv("APP_BASE_URL", "http://localhost:8000")
CHECK_INTERVAL_HOURS = int(os.getenv("CHECK_INTERVAL_HOURS", "2"))
AUTO_REPLY_MIN_RATING = int(os.getenv("AUTO_REPLY_MIN_RATING", "4"))
PORT                 = int(os.getenv("PORT", "8000"))
MOCK_MODE            = os.getenv("MOCK_MODE", "false").lower() == "true"
