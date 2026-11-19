"""Strictly DEV-only, one-time Sandbox QA scan grants.

This is intentionally separate from product entitlements and scan credits.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models import SandboxQAScanGrant, Tenant


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _assert_dev_sandbox(tenant: Tenant, company_id: str, environment_name: str) -> None:
    if (settings.ENV or "").strip().lower() == "prod":
        raise ValueError("Sandbox QA grants are disabled in PROD.")
    if (tenant.bc_environment_type or "").strip().lower() != "sandbox":
        raise ValueError("The registered tenant is not a BC sandbox.")
    if not company_id or company_id != tenant.bc_company_id:
        raise ValueError("The company does not match the registered sandbox identity.")
    if not environment_name or environment_name != tenant.bc_environment_name:
        raise ValueError("The environment does not match the registered sandbox identity.")


def issue_grant(db: Session, *, tenant: Tenant, company_id: str, environment_name: str,
                issued_by: str, expires_in_minutes: int) -> SandboxQAScanGrant:
    _assert_dev_sandbox(tenant, company_id, environment_name)
    if not 5 <= expires_in_minutes <= 60:
        raise ValueError("The QA grant lifetime must be between 5 and 60 minutes.")
    now = _now()
    grant = SandboxQAScanGrant(
        tenant_id=tenant.tenant_id, company_id=company_id, environment_name=environment_name,
        status="available", expires_at_utc=now + timedelta(minutes=expires_in_minutes),
        issued_by=issued_by, created_at_utc=now,
    )
    db.add(grant)
    try:
        db.flush()
    except IntegrityError as exc:
        raise ValueError("A Sandbox QA grant already exists for this sandbox identity.") from exc
    return grant


def claim_grant(db: Session, *, tenant: Tenant, company_id: str | None,
                environment_name: str | None, scan_id: str) -> SandboxQAScanGrant:
    _assert_dev_sandbox(tenant, company_id or "", environment_name or "")
    now = _now()
    # Conditional UPDATE is the concurrency boundary; a second request updates no row.
    statement = (
        update(SandboxQAScanGrant)
        .where(
            SandboxQAScanGrant.tenant_id == tenant.tenant_id,
            SandboxQAScanGrant.company_id == company_id,
            SandboxQAScanGrant.environment_name == environment_name,
            SandboxQAScanGrant.status == "available",
            SandboxQAScanGrant.expires_at_utc > now,
        )
        .values(status="consumed", consumed_scan_id=scan_id, consumed_at_utc=now)
    )
    if db.execute(statement).rowcount != 1:
        # Mark an expired grant explicitly, while never making it reusable.
        db.execute(update(SandboxQAScanGrant).where(
            SandboxQAScanGrant.tenant_id == tenant.tenant_id,
            SandboxQAScanGrant.company_id == company_id,
            SandboxQAScanGrant.environment_name == environment_name,
            SandboxQAScanGrant.status == "available",
            SandboxQAScanGrant.expires_at_utc <= now,
        ).values(status="expired"))
        raise ValueError("No available Sandbox QA scan grant exists for this sandbox identity.")
    grant = db.scalar(select(SandboxQAScanGrant).where(SandboxQAScanGrant.consumed_scan_id == scan_id))
    if grant is None:
        raise RuntimeError("Sandbox QA grant claim was not durable.")
    return grant


def has_available_grant(db: Session, tenant: Tenant) -> bool:
    """Read-only license hint; server-side start authorization remains authoritative."""
    if (settings.ENV or "").strip().lower() == "prod" or (tenant.bc_environment_type or "").lower() != "sandbox":
        return False
    return db.scalar(select(SandboxQAScanGrant.id).where(
        SandboxQAScanGrant.tenant_id == tenant.tenant_id,
        SandboxQAScanGrant.company_id == tenant.bc_company_id,
        SandboxQAScanGrant.environment_name == tenant.bc_environment_name,
        SandboxQAScanGrant.status == "available",
        SandboxQAScanGrant.expires_at_utc > _now(),
    ).limit(1)) is not None
