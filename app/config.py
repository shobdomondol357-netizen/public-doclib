import os
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

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production-please")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")
SITE_NAME = os.getenv("SITE_NAME", "Universal Public Document Library")
SITE_URL = os.getenv("SITE_URL", "http://localhost:8000").rstrip("/")
MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", "200000"))
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))
