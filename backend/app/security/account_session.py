from __future__ import annotations

import hashlib
from datetime import timedelta

from app.account_models import TenantMembership, UserIdentity
from app.core.settings import settings
from app.security.token import create_token, verify_token

ACCOUNT_SESSION_TOKEN_TYPE = "account_session"
ACCOUNT_SESSION_SCOPE = "account:select-tenant"
USER_TENANT_SESSION_TOKEN_TYPE = "tenant_user_session"
TENANT_DASHBOARD_SCOPE = "tenant:dashboard"


def _membership_binding(membership: TenantMembership) -> str:
    updated = membership.updated_at_utc.isoformat() if membership.updated_at_utc else ""
    material = "|".join(
        [
            str(membership.id),
            str(membership.user_identity_id),
            membership.tenant_id,
            membership.role,
            membership.status,
            updated,
        ]
    ).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def create_account_session_token(user: UserIdentity) -> str:
    return create_token(
        {
            "type": ACCOUNT_SESSION_TOKEN_TYPE,
            "scope": ACCOUNT_SESSION_SCOPE,
            "user_identity_id": user.id,
            "provider": user.provider,
            "provider_subject": user.provider_subject,
        },
        expires_delta=timedelta(minutes=max(int(settings.ACCOUNT_SESSION_MINUTES or 60), 5)),
    )


def parse_account_session_token(token: str) -> dict | None:
    payload = verify_token(token)
    if not payload:
        return None
    if payload.get("type") != ACCOUNT_SESSION_TOKEN_TYPE:
        return None
    if payload.get("scope") != ACCOUNT_SESSION_SCOPE:
        return None
    try:
        user_identity_id = int(payload.get("user_identity_id"))
    except (TypeError, ValueError):
        return None
    if user_identity_id <= 0:
        return None
    return payload


def create_user_tenant_session_token(user: UserIdentity, membership: TenantMembership) -> str:
    return create_token(
        {
            "type": USER_TENANT_SESSION_TOKEN_TYPE,
            "scope": TENANT_DASHBOARD_SCOPE,
            "tenant_id": membership.tenant_id,
            "user_identity_id": user.id,
            "membership_id": membership.id,
            "tenant_role": membership.role,
            "membership_binding": _membership_binding(membership),
        },
        expires_delta=timedelta(minutes=15),
    )


def parse_user_tenant_session_token(token: str) -> dict | None:
    payload = verify_token(token)
    if not payload:
        return None
    if payload.get("type") != USER_TENANT_SESSION_TOKEN_TYPE:
        return None
    if payload.get("scope") != TENANT_DASHBOARD_SCOPE:
        return None
    tenant_id = str(payload.get("tenant_id") or "").strip()
    try:
        user_identity_id = int(payload.get("user_identity_id"))
        membership_id = int(payload.get("membership_id"))
    except (TypeError, ValueError):
        return None
    if not tenant_id or user_identity_id <= 0 or membership_id <= 0:
        return None
    return payload


def verify_user_tenant_session_payload(payload: dict, membership: TenantMembership) -> bool:
    if membership.status != "active":
        return False
    if int(payload.get("membership_id") or 0) != membership.id:
        return False
    if int(payload.get("user_identity_id") or 0) != membership.user_identity_id:
        return False
    if str(payload.get("tenant_id") or "") != membership.tenant_id:
        return False
    if str(payload.get("tenant_role") or "") != membership.role:
        return False
    return str(payload.get("membership_binding") or "") == _membership_binding(membership)
