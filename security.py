"""
security.py

Password hashing (PBKDF2-HMAC-SHA256, stdlib only) and JWT session
tokens (PyJWT) for real authentication on top of the SQLite backend.
"""

import os
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "60"))

PBKDF2_ITERATIONS = 200_000


def _jwt_secret() -> str:
    """Read lazily so seed.py (which only hashes passwords) needn't set it."""
    secret = os.environ.get("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET is not set. Add it to .env (see .env.example).")
    return secret


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ITERATIONS)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, digest_hex = password_hash.split("$")
    except ValueError:
        return False
    expected = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ITERATIONS)
    return hmac.compare_digest(expected.hex(), digest_hex)


def create_access_token(customer_id: str) -> str:
    payload = {
        "sub": customer_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Returns customer_id if valid, else None."""
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
