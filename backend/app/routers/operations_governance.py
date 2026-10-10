from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db import SessionLocal
from app.operations_governance_models import TenantFeatureFlag, TenantSupportAccessGrant
from app.routers.membership_admin import _tenant_user_principal
from app.services.operations_governance_service import (
    audit_feed,
    create_data_lifecycle_request,
    grant_diagnostics_support,
    retention_policy,
    revoke_support_grant,
    support_diagnostics_active,
)
from app.services.tenant_membership_admin_service import require_tenant_admin

router = APIRouter(tags=["operations-governance"])


class SupportGrantRequest(BaseModel):
    hours: int = Field(default=24, ge=1, le=168)
    reason: str = Field(min_length=3, max_length=255)


class DataLifecycleRequestBody(BaseModel):
    request_type: str
    reason: str | None = Field(default=None, max_length=255)


@router.get("/account/tenant/support-access")
def read_support_access(authorization: str | None = Header(default=None, alias="Authorization")) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        require_tenant_admin(db, user_identity_id=user_id, tenant_id=tenant_id)
        rows = db.scalars(select(TenantSupportAccessGrant).where(
            TenantSupportAccessGrant.tenant_id == tenant_id
        ).order_by(TenantSupportAccessGrant.created_at_utc.desc()).limit(50)).all()
        return {
            "tenant_id": tenant_id,
            "diagnostics_active": support_diagnostics_active(db, tenant_id),
            "grants": [{"id": row.id, "access_mode": row.access_mode, "status": row.status,
                        "valid_from_utc": row.valid_from_utc, "valid_until_utc": row.valid_until_utc,
                        "reason": row.reason} for row in rows],
        }


@router.post("/account/tenant/support-access")
def enable_support_diagnostics(payload: SupportGrantRequest,
                               authorization: str | None = Header(default=None, alias="Authorization")) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        require_tenant_admin(db, user_identity_id=user_id, tenant_id=tenant_id)
        try:
            grant = grant_diagnostics_support(db, tenant_id=tenant_id, user_identity_id=user_id,
                                              hours=payload.hours, reason=payload.reason)
            db.commit()
            return {"status": "active", "grant_id": grant.id, "access_mode": "diagnostics",
                    "valid_until_utc": grant.valid_until_utc}
        except ValueError as exc:
            db.rollback(); raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/account/tenant/support-access/{grant_id}")
def disable_support_diagnostics(grant_id: int,
                                authorization: str | None = Header(default=None, alias="Authorization")) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        require_tenant_admin(db, user_identity_id=user_id, tenant_id=tenant_id)
        grant = db.get(TenantSupportAccessGrant, grant_id)
        if grant is None or grant.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Support access grant not found.")
        try:
            revoke_support_grant(db, grant_id=grant_id, user_identity_id=user_id)
            db.commit(); return {"status": "revoked", "grant_id": grant_id}
        except ValueError as exc:
            db.rollback(); raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/account/tenant/audit")
def read_tenant_audit(limit: int = 100,
                      authorization: str | None = Header(default=None, alias="Authorization")) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        require_tenant_admin(db, user_identity_id=user_id, tenant_id=tenant_id)
        return {"tenant_id": tenant_id, "events": audit_feed(db, tenant_id=tenant_id, limit=limit)}


@router.get("/account/tenant/data-policy")
def read_data_policy(authorization: str | None = Header(default=None, alias="Authorization")) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        require_tenant_admin(db, user_identity_id=user_id, tenant_id=tenant_id)
    return {"tenant_id": tenant_id, "policy": retention_policy()}


@router.post("/account/tenant/data-lifecycle")
def request_data_lifecycle(payload: DataLifecycleRequestBody,
                           authorization: str | None = Header(default=None, alias="Authorization")) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        require_tenant_admin(db, user_identity_id=user_id, tenant_id=tenant_id)
        try:
            row = create_data_lifecycle_request(db, tenant_id=tenant_id, request_type=payload.request_type,
                                                user_identity_id=user_id, reason=payload.reason)
            db.commit(); return {"request_id": row.id, "request_type": row.request_type, "status": row.status}
        except ValueError as exc:
            db.rollback(); raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/account/tenant/feature-flags")
def read_feature_flags(authorization: str | None = Header(default=None, alias="Authorization")) -> dict:
    _, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        rows = db.scalars(select(TenantFeatureFlag).where(TenantFeatureFlag.tenant_id == tenant_id).order_by(TenantFeatureFlag.flag_key.asc())).all()
        return {"tenant_id": tenant_id, "flags": [{"key": row.flag_key, "enabled": row.enabled} for row in rows]}
