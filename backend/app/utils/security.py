from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import os

from jose import jwt

from app.config import settings

PBKDF2_PREFIX = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 260000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    encoded_salt = base64.b64encode(salt).decode("ascii")
    encoded_digest = base64.b64encode(digest).decode("ascii")
    return f"{PBKDF2_PREFIX}${PBKDF2_ITERATIONS}${encoded_salt}${encoded_digest}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        prefix, iterations, encoded_salt, encoded_digest = hashed_password.split("$", 3)
        if prefix != PBKDF2_PREFIX:
            return False
        salt = base64.b64decode(encoded_salt)
        expected = base64.b64decode(encoded_digest)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, roles: list[str], permissions: list[str], user_id: int | None = None) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "roles": roles, "permissions": permissions, "type": "access", "exp": expires_at}
    if user_id is not None:
        payload["uid"] = user_id
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {"sub": subject, "type": "refresh", "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
