from __future__ import annotations

import hmac
import secrets
from hashlib import sha256

CSRF_COOKIE_NAME = "bcs_csrf"
CSRF_FORM_FIELD = "csrf_token"


def _signature(secret_key: str, nonce: str) -> str:
    return hmac.new(secret_key.encode("utf-8"), nonce.encode("utf-8"), sha256).hexdigest()


def create_csrf_token(secret_key: str) -> str:
    nonce = secrets.token_urlsafe(24)
    return f"{nonce}.{_signature(secret_key, nonce)}"


def verify_csrf_token(secret_key: str, cookie_token: str | None, supplied_token: str | None) -> bool:
    if not cookie_token or not supplied_token:
        return False
    if not hmac.compare_digest(cookie_token, supplied_token):
        return False
    if "." not in cookie_token:
        return False
    nonce, provided_signature = cookie_token.rsplit(".", 1)
    if not nonce or not provided_signature:
        return False
    expected_signature = _signature(secret_key, nonce)
    return hmac.compare_digest(provided_signature, expected_signature)
