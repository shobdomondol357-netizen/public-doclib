import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import AdminSession
from .config import ADMIN_PASSWORD, SECRET_KEY

def create_session(db: Session) -> str:
    token = secrets.token_urlsafe(32)
    s = AdminSession(token=token, expires_at=datetime.utcnow() + timedelta(days=7))
    db.add(s)
    db.commit()
    return token

def is_admin(db: Session, token: str) -> bool:
    if not token:
        return False
    s = db.query(AdminSession).filter(AdminSession.token == token).first()
    if not s:
        return False
    if s.expires_at < datetime.utcnow():
        db.delete(s)
        db.commit()
        return False
    return True

def login_ok(password: str) -> bool:
    return password == ADMIN_PASSWORD

def revoke(db: Session, token: str):
    s = db.query(AdminSession).filter(AdminSession.token == token).first()
    if s:
        db.delete(s)
        db.commit()
