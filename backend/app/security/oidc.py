from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock

import httpx
from fastapi import HTTPException
from jose import JWTError, jwt

from app.core.settings import settings


@dataclass(frozen=True)
class VerifiedOIDCIdentity:
    provider: str
    subject: str
    email: str
    display_name: str | None


_jwks_cache: dict[str, object] = {"value": None, "expires_at": 0.0}
_jwks_lock = Lock()
_JWKS_TTL_SECONDS = 300


def _require_oidc_config() -> tuple[str, str, str]:
    if not settings.OIDC_ENABLED:
        raise HTTPException(status_code=503, detail="Customer identity provider is not configured.")
    issuer = (settings.OIDC_ISSUER or "").strip().rstrip("/")
    audience = (settings.OIDC_AUDIENCE or "").strip()
    jwks_url = (settings.OIDC_JWKS_URL or "").strip()
    if not issuer or not audience or not jwks_url:
        raise HTTPException(status_code=503, detail="Customer identity provider is not configured.")
    return issuer, audience, jwks_url


def _load_jwks(jwks_url: str) -> dict:
    now = time.monotonic()
    with _jwks_lock:
        cached = _jwks_cache.get("value")
        if isinstance(cached, dict) and float(_jwks_cache.get("expires_at") or 0) > now:
            return cached

    try:
        response = httpx.get(jwks_url, timeout=float(settings.OIDC_HTTP_TIMEOUT_SECONDS or 5.0))
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Customer identity provider is unavailable.") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("keys"), list):
        raise HTTPException(status_code=503, detail="Customer identity provider returned invalid signing keys.")
    with _jwks_lock:
        _jwks_cache["value"] = payload
        _jwks_cache["expires_at"] = now + _JWKS_TTL_SECONDS
    return payload


def _select_signing_key(token: str, jwks: dict) -> dict:
    try:
        header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid identity token.") from exc
    kid = str(header.get("kid") or "")
    alg = str(header.get("alg") or "")
    if alg not in {"RS256", "RS384", "RS512"}:
        raise HTTPException(status_code=401, detail="Unsupported identity token algorithm.")
    candidates = [key for key in jwks.get("keys", []) if isinstance(key, dict)]
    if kid:
        candidates = [key for key in candidates if str(key.get("kid") or "") == kid]
    if len(candidates) != 1:
        raise HTTPException(status_code=401, detail="Identity token signing key could not be resolved.")
    return candidates[0]


def verify_oidc_bearer_token(token: str) -> VerifiedOIDCIdentity:
    issuer, audience, jwks_url = _require_oidc_config()
    normalized_token = (token or "").strip()
    if not normalized_token:
        raise HTTPException(status_code=401, detail="Missing identity token.")
    jwks = _load_jwks(jwks_url)
    signing_key = _select_signing_key(normalized_token, jwks)
    try:
        payload = jwt.decode(
            normalized_token,
            signing_key,
            algorithms=[str(signing_key.get("alg") or "RS256")],
            audience=audience,
            issuer=issuer,
            options={"verify_at_hash": False},
        )
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid identity token.") from exc

    subject = str(payload.get("sub") or "").strip()
    email_claim = (settings.OIDC_EMAIL_CLAIM or "email").strip()
    name_claim = (settings.OIDC_NAME_CLAIM or "name").strip()
    email = str(payload.get(email_claim) or "").strip()
    email_verified = payload.get("email_verified")
    if not subject or not email:
        raise HTTPException(status_code=403, detail="Verified identity is missing required claims.")
    if email_verified is False:
        raise HTTPException(status_code=403, detail="Identity email verification is required.")
    return VerifiedOIDCIdentity(
        provider=(settings.OIDC_PROVIDER_KEY or "oidc").strip().lower() or "oidc",
        subject=subject,
        email=email,
        display_name=str(payload.get(name_claim) or "").strip() or None,
    )
