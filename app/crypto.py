import base64, hashlib, os
from cryptography.fernet import Fernet, InvalidToken

def _fernet():
    key = base64.urlsafe_b64encode(hashlib.sha256((os.getenv("SECRET_KEY","") or "dev-secret").encode()).digest())
    return Fernet(key)

def encrypt(text: str) -> str:
    if not text:
        return ""
    return _fernet().encrypt(text.encode()).decode()

def decrypt(text: str) -> str:
    if not text:
        return ""
    try:
        return _fernet().decrypt(text.encode()).decode()
    except (InvalidToken, Exception):
        # backward compat: maybe plaintext
        return text
