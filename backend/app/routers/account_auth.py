from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.account_models import TenantMembership, UserIdentity
from app.db import SessionLocal
from app.models import AdminAuditEvent
from app.security.account_session import (
    ACCOUNT_SESSION_SCOPE,
    create_account_session_token,
    create_user_tenant_session_token,
    parse_account_session_token,
)
from app.security.oidc import verify_oidc_bearer_token
from app.services.account_membership_service import (
    get_or_create_user_identity,
    list_active_memberships,
    require_active_membership,
)

router = APIRouter(tags=["account-auth"])


class AccountSessionResponse(BaseModel):
    session_token: str
    token_type: str = "Bearer"
    scope: str = ACCOUNT_SESSION_SCOPE
    expires_in_seconds: int
    user_identity_id: int
    email: str
    display_name: str | None = None
    tenant_count: int
    requires_tenant_selection: bool
    auto_select_tenant_id: str | None = None


class AccountTenantSummary(BaseModel):
    tenant_id: str
    environment_name: str
    role: str
    membership_status: str
    tenant_status: str
    current_plan: str
    license_status: str


class AccountTenantListResponse(BaseModel):
    user_identity_id: int
    tenants: list[AccountTenantSummary]


class TenantSwitchRequest(BaseModel):
    tenant_id: str


class TenantSwitchResponse(BaseModel):
    tenant_id: str
    session_token: str
    token_type: str = "Bearer"
    expires_in_seconds: int = 900
    scope: str = "tenant:dashboard"
    role: str
    user_identity_id: int


def _bearer_value(authorization: str | None) -> str:
    raw = (authorization or "").strip()
    scheme, separator, token = raw.partition(" ")
    if scheme.lower() != "bearer" or not separator or not token.strip():
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header.")
    return token.strip()


def _load_account_principal(db, authorization: str | None) -> tuple[UserIdentity, dict]:
    token = _bearer_value(authorization)
    payload = parse_account_session_token(token)
    if payload is None:
        raise HTTPException(status_code=403, detail="Invalid account session.")
    user = db.get(UserIdentity, int(payload["user_identity_id"]))
    if user is None or user.status != "active":
        raise HTTPException(status_code=403, detail="Account access is not active.")
    if str(payload.get("provider") or "") != user.provider:
        raise HTTPException(status_code=403, detail="Invalid account session.")
    if str(payload.get("provider_subject") or "") != user.provider_subject:
        raise HTTPException(status_code=403, detail="Invalid account session.")
    return user, payload


def _audit_tenant_session(db, *, user: UserIdentity, membership: TenantMembership) -> None:
    db.add(
        AdminAuditEvent(
            admin_username=f"user:{user.id}",
            action="tenant_session.create",
            target_type="tenant_membership",
            target_id=str(membership.id),
            details_json=json.dumps(
                {
                    "tenant_id": membership.tenant_id,
                    "role": membership.role,
                    "user_identity_id": user.id,
                },
                sort_keys=True,
            ),
            created_at_utc=datetime.now(timezone.utc),
        )
    )


@router.post("/auth/account/session", response_model=AccountSessionResponse)
def create_account_session(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> AccountSessionResponse:
    provider_token = _bearer_value(authorization)
    identity = verify_oidc_bearer_token(provider_token)
    with SessionLocal() as db:
        user = get_or_create_user_identity(
            db,
            provider=identity.provider,
            provider_subject=identity.subject,
            email=identity.email,
            display_name=identity.display_name,
        )
        db.flush()
        memberships = list_active_memberships(db, user.id)
        session_token = create_account_session_token(user)
        user_id = user.id
        email = user.email_normalized
        display_name = user.display_name
        db.commit()

    tenant_count = len(memberships)
    return AccountSessionResponse(
        session_token=session_token,
        expires_in_seconds=3600,
        user_identity_id=user_id,
        email=email,
        display_name=display_name,
        tenant_count=tenant_count,
        requires_tenant_selection=tenant_count > 1,
        auto_select_tenant_id=memberships[0]["tenant_id"] if tenant_count == 1 else None,
    )


@router.get("/auth/account/tenants", response_model=AccountTenantListResponse)
def list_account_tenants(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> AccountTenantListResponse:
    with SessionLocal() as db:
        user, _ = _load_account_principal(db, authorization)
        memberships = list_active_memberships(db, user.id)
        return AccountTenantListResponse(
            user_identity_id=user.id,
            tenants=[AccountTenantSummary(**item) for item in memberships],
        )


@router.post("/auth/account/tenant-session", response_model=TenantSwitchResponse)
def create_account_tenant_session(
    payload: TenantSwitchRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> TenantSwitchResponse:
    with SessionLocal() as db:
        user, _ = _load_account_principal(db, authorization)
        membership = require_active_membership(
            db,
            user_identity_id=user.id,
            tenant_id=payload.tenant_id.strip(),
        )
        # Re-load by id inside the same session so the session binding always reflects
        # the authoritative role/status/update timestamp at mint time.
        membership = db.scalar(select(TenantMembership).where(TenantMembership.id == membership.id))
        if membership is None:
            raise HTTPException(status_code=403, detail="Tenant membership is not active.")
        tenant_token = create_user_tenant_session_token(user, membership)
        _audit_tenant_session(db, user=user, membership=membership)
        db.commit()
        return TenantSwitchResponse(
            tenant_id=membership.tenant_id,
            session_token=tenant_token,
            role=membership.role,
            user_identity_id=user.id,
        )
