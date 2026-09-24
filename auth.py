"""JWT and bcrypt auth; existing $2a$/$2b$ password hashes remain valid."""
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
import jwt
import bcrypt
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "")
if len(SECRET_KEY.encode("utf-8")) < 32 or SECRET_KEY == "zein-academy-secret-key-change-in-production":
    raise RuntimeError("Set a private SECRET_KEY of at least 32 bytes in the server environment (see .env.example)")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
if ALGORITHM not in {"HS256", "HS384", "HS512"}:
    raise RuntimeError("ALGORITHM must be HS256, HS384 or HS512")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "129600"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # Original passlib/bcrypt silently truncated to 72 bytes. Preserve login
        # compatibility, while newly set passwords are explicitly validated.
        return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("ascii"))
    except (ValueError, TypeError, UnicodeError):
        return False


def hash_password(password: str) -> str:
    raw = password.encode("utf-8")
    if not 8 <= len(raw) <= 72:
        raise ValueError("Пароль должен занимать от 8 до 72 байт UTF-8")
    return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=12)).decode("ascii")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["exp", "sub"]})
    except jwt.InvalidTokenError:
        return None
