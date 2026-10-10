from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.tenant_access_models import TenantAccessState

TENANT_STATUS_ACTIVE = "active"
TENANT_STATUS_SUSPENDED = "suspended"
TENANT_STATUS_DEACTIVATED = "deactivated"
TENANT_ACCESS_STATUSES = {
    TENANT_STATUS_ACTIVE,
    TENANT_STATUS_SUSPENDED,
    TENANT_STATUS_DEACTIVATED,
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_tenant_status(value: str | None) -> str:
    normalized = (value or TENANT_STATUS_ACTIVE).strip().lower()
    if normalized not in TENANT_ACCESS_STATUSES:
        raise ValueError(f"Unsupported tenant status: {value}")
    return normalized


def get_tenant_access_state(db: Session, tenant_id: str) -> TenantAccessState | None:
    return db.scalar(select(TenantAccessState).where(TenantAccessState.tenant_id == tenant_id))


def get_tenant_status(db: Session, tenant_id: str) -> str:
    state = get_tenant_access_state(db, tenant_id)
    if state is None:
        # Backward-compatible default for tenants created before E1.
        return TENANT_STATUS_ACTIVE
    return normalize_tenant_status(state.status)


def ensure_tenant_access_state(db: Session, tenant_id: str) -> TenantAccessState:
    state = get_tenant_access_state(db, tenant_id)
    if state is not None:
        return state
    state = TenantAccessState(
        tenant_id=tenant_id,
        status=TENANT_STATUS_ACTIVE,
        reason=None,
        updated_by="system",
        updated_at_utc=utc_now(),
    )
    db.add(state)
    db.flush()
    return state


def set_tenant_status(
    db: Session,
    *,
    tenant_id: str,
    status: str,
    reason: str | None = None,
    updated_by: str | None = None,
) -> TenantAccessState:
    normalized = normalize_tenant_status(status)
    state = ensure_tenant_access_state(db, tenant_id)
    state.status = normalized
    state.reason = (reason or "").strip() or None
    state.updated_by = (updated_by or "").strip() or None
    state.updated_at_utc = utc_now()
    db.flush()
    return state


def enforce_tenant_is_active(db: Session, tenant_id: str) -> str:
    status = get_tenant_status(db, tenant_id)
    if status != TENANT_STATUS_ACTIVE:
        # Do not disclose suspension/deactivation details to the caller.
        raise HTTPException(status_code=403, detail="Tenant access is not active.")
    return status
