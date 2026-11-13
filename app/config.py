import os, secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if os.getenv("VERCEL"):
    DATA_DIR = Path("/tmp/doclib-data")
else:
    DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'doclib.db'}")
# normalize postgres url
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    import sys
    print("WARNING: SECRET_KEY not set; using insecure dev key", file=sys.stderr)
    SECRET_KEY = "dev-insecure-secret-change-me"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
SYNC_SECRET = os.getenv("SYNC_SECRET", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")
SITE_NAME = os.getenv("SITE_NAME", "Universal Public Document Library")
SITE_URL = os.getenv("SITE_URL", "http://localhost:8000").rstrip("/")
MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", "200000"))
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))
LOGIN_RATE_LIMIT_PER_MIN = int(os.getenv("LOGIN_RATE_LIMIT_PER_MIN", "10"))

def is_production():
    return bool(os.getenv("RENDER") or os.getenv("VERCEL") or os.getenv("PRODUCTION"))

# Auto-generate sync secret for dev if missing (not persistent across instances)
if not SYNC_SECRET:
    SYNC_SECRET = secrets.token_urlsafe(32) if not is_production() else ""
    if not SYNC_SECRET:
        import sys
        print("WARNING: SYNC_SECRET not set; automated sync disabled", file=sys.stderr)
