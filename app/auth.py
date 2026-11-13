import secrets, hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import AdminSession
from .config import ADMIN_PASSWORD, SECRET_KEY
import os

def _strong_password_configured() -> bool:
    pw = ADMIN_PASSWORD or ""
    if len(pw) < 12:
        return False
    # reject obvious defaults
    if pw.lower() in ("admin", "password", "123456", "changeme", "change-me"):
        return False
    return True

def login_ok(password: str) -> bool:
    if not _strong_password_configured():
        return False
    return secrets.compare_digest(password or "", ADMIN_PASSWORD)

def create_session(db: Session) -> str:
    token = secrets.token_urlsafe(32)
    s = AdminSession(token=token, expires_at=datetime.utcnow() + timedelta(days=7))
    db.add(s)
    db.commit()
    return token

def is_admin(db: Session, token: str) -> bool:
    if not token or not _strong_password_configured():
        return False
    s = db.query(AdminSession).filter(AdminSession.token == token).first()
    if not s:
        return False
    if s.expires_at < datetime.utcnow():
        db.delete(s)
        db.commit()
        return False
    return True

def revoke(db: Session, token: str):
    s = db.query(AdminSession).filter(AdminSession.token == token).first()
    if s:
        db.delete(s)
        db.commit()

def admin_enabled() -> bool:
    return _strong_password_configured()

def verify_sync_secret(provided: str) -> bool:
    from .config import SYNC_SECRET
    if not SYNC_SECRET or not provided:
        return False
    return secrets.compare_digest(provided, SYNC_SECRET)
