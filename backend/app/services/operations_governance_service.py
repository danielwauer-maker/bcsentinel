from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import func, select

from app.models import AdminAuditEvent, Tenant
from app.operations_governance_models import (
    ProductTelemetryEvent,
    TenantDataLifecycleRequest,
    TenantFeatureFlag,
    TenantSupportAccessGrant,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _audit(db, *, actor: str, action: str, target_type: str, target_id: str, details: dict) -> None:
    db.add(AdminAuditEvent(
        admin_username=actor[:120], action=action[:80], target_type=target_type[:60], target_id=str(target_id)[:120],
        details_json=json.dumps(details, sort_keys=True, default=str), created_at_utc=utc_now(),
    ))


def grant_diagnostics_support(db, *, tenant_id: str, user_identity_id: int, hours: int, reason: str) -> TenantSupportAccessGrant:
    if db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id)) is None:
        raise ValueError("Tenant not found.")
    if not reason.strip():
        raise ValueError("Support access reason is required.")
    now = utc_now()
    grant = TenantSupportAccessGrant(
        tenant_id=tenant_id, access_mode="diagnostics", status="active", valid_from_utc=now,
        valid_until_utc=now + timedelta(hours=max(1, min(int(hours), 168))), reason=reason.strip(),
        granted_by_user_identity_id=user_identity_id, created_at_utc=now,
    )
    db.add(grant); db.flush()
    _audit(db, actor=f"user:{user_identity_id}", action="support_access.grant", target_type="support_access", target_id=str(grant.id),
           details={"tenant_id": tenant_id, "access_mode": "diagnostics", "valid_until_utc": grant.valid_until_utc})
    return grant


def revoke_support_grant(db, *, grant_id: int, user_identity_id: int) -> TenantSupportAccessGrant:
    grant = db.get(TenantSupportAccessGrant, grant_id)
    if grant is None:
        raise ValueError("Support access grant not found.")
    grant.status = "revoked"; grant.revoked_by_user_identity_id = user_identity_id; grant.revoked_at_utc = utc_now()
    _audit(db, actor=f"user:{user_identity_id}", action="support_access.revoke", target_type="support_access", target_id=str(grant.id),
           details={"tenant_id": grant.tenant_id})
    return grant


def support_diagnostics_active(db, tenant_id: str, at_utc: datetime | None = None) -> bool:
    moment = at_utc or utc_now()
    return db.scalar(select(func.count(TenantSupportAccessGrant.id)).where(
        TenantSupportAccessGrant.tenant_id == tenant_id,
        TenantSupportAccessGrant.access_mode == "diagnostics",
        TenantSupportAccessGrant.status == "active",
        TenantSupportAccessGrant.valid_from_utc <= moment,
        TenantSupportAccessGrant.valid_until_utc > moment,
    )) > 0


def set_feature_flag(db, *, tenant_id: str, flag_key: str, enabled: bool, actor: str, config: dict | None = None) -> TenantFeatureFlag:
    key = (flag_key or "").strip().lower()
    if not key or len(key) > 100:
        raise ValueError("Invalid feature flag key.")
    row = db.scalar(select(TenantFeatureFlag).where(TenantFeatureFlag.tenant_id == tenant_id, TenantFeatureFlag.flag_key == key))
    if row is None:
        row = TenantFeatureFlag(tenant_id=tenant_id, flag_key=key, enabled=bool(enabled), config_json="{}", updated_by=actor, updated_at_utc=utc_now())
        db.add(row)
    row.enabled = bool(enabled); row.config_json = json.dumps(config or {}, sort_keys=True); row.updated_by = actor; row.updated_at_utc = utc_now()
    db.flush()
    _audit(db, actor=actor, action="feature_flag.set", target_type="tenant_feature_flag", target_id=str(row.id),
           details={"tenant_id": tenant_id, "flag_key": key, "enabled": bool(enabled)})
    return row


def feature_enabled(db, *, tenant_id: str, flag_key: str, default: bool = False) -> bool:
    row = db.scalar(select(TenantFeatureFlag).where(TenantFeatureFlag.tenant_id == tenant_id, TenantFeatureFlag.flag_key == flag_key.strip().lower()))
    return bool(row.enabled) if row is not None else bool(default)


def create_data_lifecycle_request(db, *, tenant_id: str, request_type: str, user_identity_id: int, reason: str | None = None) -> TenantDataLifecycleRequest:
    kind = (request_type or "").strip().lower()
    if kind not in {"export", "delete"}:
        raise ValueError("request_type must be export or delete.")
    pending = db.scalar(select(TenantDataLifecycleRequest).where(
        TenantDataLifecycleRequest.tenant_id == tenant_id,
        TenantDataLifecycleRequest.request_type == kind,
        TenantDataLifecycleRequest.status.in_(["requested", "processing"]),
    ))
    if pending is not None:
        raise ValueError("A matching data lifecycle request is already pending.")
    row = TenantDataLifecycleRequest(
        tenant_id=tenant_id, request_type=kind, status="requested", requested_by_user_identity_id=user_identity_id,
        reason=(reason or "").strip() or None, requested_at_utc=utc_now(),
    )
    db.add(row); db.flush()
    _audit(db, actor=f"user:{user_identity_id}", action=f"data_lifecycle.{kind}_request", target_type="tenant_data_lifecycle_request", target_id=str(row.id),
           details={"tenant_id": tenant_id})
    return row


def record_telemetry(db, *, event_name: str, outcome: str = "info", tenant_id: str | None = None,
                     duration_ms: int | None = None, metadata: dict | None = None) -> ProductTelemetryEvent:
    safe_metadata = {}
    for key, value in (metadata or {}).items():
        if key.lower() in {"email", "name", "token", "password", "api_token", "authorization"}:
            continue
        safe_metadata[str(key)[:80]] = value
    row = ProductTelemetryEvent(
        tenant_id=tenant_id, event_name=event_name.strip()[:100], outcome=outcome.strip().lower()[:30],
        duration_ms=max(int(duration_ms), 0) if duration_ms is not None else None,
        metadata_json=json.dumps(safe_metadata, sort_keys=True, default=str), occurred_at_utc=utc_now(),
    )
    db.add(row); db.flush(); return row


def retention_policy() -> dict:
    path = Path(__file__).resolve().parents[3] / "config" / "data-retention.json"
    return json.loads(path.read_text(encoding="utf-8"))


def audit_feed(db, *, tenant_id: str, limit: int = 100) -> list[dict]:
    rows = db.scalars(select(AdminAuditEvent).where(
        (AdminAuditEvent.target_id == tenant_id) | (AdminAuditEvent.details_json.contains(tenant_id))
    ).order_by(AdminAuditEvent.created_at_utc.desc()).limit(max(1, min(limit, 200)))).all()
    return [{"id": r.id, "action": r.action, "target_type": r.target_type, "target_id": r.target_id,
             "created_at_utc": r.created_at_utc, "actor": r.admin_username} for r in rows]
