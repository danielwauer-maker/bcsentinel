from __future__ import annotations

import hashlib
from datetime import timedelta

from app.models import Tenant
from app.security.token import create_token, verify_token

TENANT_SESSION_TOKEN_TYPE = "tenant_dashboard_session"
TENANT_SESSION_SCOPE = "tenant:dashboard"
TENANT_SESSION_ROLE = "dashboard_runtime"
TENANT_SESSION_MINUTES = 15
TENANT_SESSION_PREFIX = "session:"


def _token_binding(tenant: Tenant) -> str:
    material = (tenant.api_token_hash or tenant.api_token or "").encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def create_tenant_session_token(tenant: Tenant) -> str:
    return create_token(
        {
            "type": TENANT_SESSION_TOKEN_TYPE,
            "scope": TENANT_SESSION_SCOPE,
            "role": TENANT_SESSION_ROLE,
            "tenant_id": tenant.tenant_id,
            "credential_binding": _token_binding(tenant),
        },
        expires_delta=timedelta(minutes=TENANT_SESSION_MINUTES),
    )


def parse_tenant_session_token(token: str) -> dict | None:
    payload = verify_token(token)
    if not payload:
        return None
    if payload.get("type") != TENANT_SESSION_TOKEN_TYPE:
        return None
    if payload.get("scope") != TENANT_SESSION_SCOPE:
        return None
    if payload.get("role") != TENANT_SESSION_ROLE:
        return None
    tenant_id = str(payload.get("tenant_id") or "").strip()
    if not tenant_id:
        return None
    return payload


def verify_tenant_session_token(token: str, tenant: Tenant) -> bool:
    payload = parse_tenant_session_token(token)
    if not payload:
        return False
    if str(payload.get("tenant_id") or "") != tenant.tenant_id:
        return False
    return str(payload.get("credential_binding") or "") == _token_binding(tenant)


def session_credential(token: str) -> str:
    return f"{TENANT_SESSION_PREFIX}{token}"


def is_session_credential(value: str) -> bool:
    return value.startswith(TENANT_SESSION_PREFIX)


def unwrap_session_credential(value: str) -> str:
    return value[len(TENANT_SESSION_PREFIX) :]
