from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.account_models import TenantMembership, UserIdentity
from app.models import Tenant
from app.services.tenant_access_service import get_tenant_status

ALLOWED_MEMBERSHIP_ROLES = {"VIEWER", "SETUP", "SCHEDULER", "ADMIN"}
ALLOWED_MEMBERSHIP_STATES = {"invited", "active", "suspended", "revoked"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_email(value: str) -> str:
    return (value or "").strip().casefold()


def normalize_role(value: str) -> str:
    role = (value or "").strip().upper()
    if role not in ALLOWED_MEMBERSHIP_ROLES:
        raise ValueError(f"Unsupported tenant membership role: {value}")
    return role


def get_or_create_user_identity(
    db: Session,
    *,
    provider: str,
    provider_subject: str,
    email: str,
    display_name: str | None = None,
) -> UserIdentity:
    normalized_provider = (provider or "").strip().lower()
    normalized_subject = (provider_subject or "").strip()
    normalized_email = normalize_email(email)
    if not normalized_provider or not normalized_subject or not normalized_email:
        raise ValueError("provider, provider_subject and email are required")

    row = db.scalar(
        select(UserIdentity).where(
            UserIdentity.provider == normalized_provider,
            UserIdentity.provider_subject == normalized_subject,
        )
    )
    now = utc_now()
    if row is None:
        row = UserIdentity(
            provider=normalized_provider,
            provider_subject=normalized_subject,
            email_normalized=normalized_email,
            display_name=(display_name or "").strip() or None,
            status="active",
            created_at_utc=now,
            updated_at_utc=now,
            last_login_at_utc=now,
        )
        db.add(row)
        db.flush()
        return row

    if row.status != "active":
        raise HTTPException(status_code=403, detail="Account access is not active.")
    row.email_normalized = normalized_email
    if display_name is not None:
        row.display_name = display_name.strip() or None
    row.last_login_at_utc = now
    row.updated_at_utc = now
    db.flush()
    return row


def upsert_tenant_membership(
    db: Session,
    *,
    user_identity_id: int,
    tenant_id: str,
    role: str,
    status: str = "active",
    invited_by: str | None = None,
) -> TenantMembership:
    normalized_role = normalize_role(role)
    normalized_status = (status or "").strip().lower()
    if normalized_status not in ALLOWED_MEMBERSHIP_STATES:
        raise ValueError(f"Unsupported tenant membership state: {status}")
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
    if tenant is None:
        raise ValueError("Tenant not found")

    row = db.scalar(
        select(TenantMembership).where(
            TenantMembership.user_identity_id == user_identity_id,
            TenantMembership.tenant_id == tenant_id,
        )
    )
    now = utc_now()
    if row is None:
        row = TenantMembership(
            user_identity_id=user_identity_id,
            tenant_id=tenant_id,
            role=normalized_role,
            status=normalized_status,
            invited_by=(invited_by or "").strip() or None,
            invited_at_utc=now,
            accepted_at_utc=now if normalized_status == "active" else None,
            created_at_utc=now,
            updated_at_utc=now,
        )
        db.add(row)
        db.flush()
        return row

    row.role = normalized_role
    row.status = normalized_status
    row.updated_at_utc = now
    if normalized_status == "active" and row.accepted_at_utc is None:
        row.accepted_at_utc = now
    if normalized_status == "revoked":
        row.revoked_at_utc = now
    db.flush()
    return row


def list_active_memberships(db: Session, user_identity_id: int) -> list[dict]:
    rows = db.scalars(
        select(TenantMembership)
        .where(
            TenantMembership.user_identity_id == user_identity_id,
            TenantMembership.status == "active",
        )
        .order_by(TenantMembership.tenant_id.asc())
    ).all()
    result: list[dict] = []
    for membership in rows:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == membership.tenant_id))
        if tenant is None:
            continue
        if get_tenant_status(db, tenant.tenant_id) != "active":
            continue
        result.append(
            {
                "tenant_id": tenant.tenant_id,
                "environment_name": tenant.environment_name,
                "role": membership.role,
                "membership_status": membership.status,
                "tenant_status": "active",
                "current_plan": tenant.current_plan,
                "license_status": tenant.license_status,
            }
        )
    return result


def require_active_membership(
    db: Session,
    *,
    user_identity_id: int,
    tenant_id: str,
) -> TenantMembership:
    membership = db.scalar(
        select(TenantMembership).where(
            TenantMembership.user_identity_id == user_identity_id,
            TenantMembership.tenant_id == tenant_id,
        )
    )
    if membership is None or membership.status != "active":
        raise HTTPException(status_code=403, detail="Tenant membership is not active.")
    if get_tenant_status(db, tenant_id) != "active":
        raise HTTPException(status_code=403, detail="Tenant access is not active.")
    return membership
