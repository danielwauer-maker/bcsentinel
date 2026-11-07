from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.customer_runtime_models import TenantBillingProfile, TenantConnectionDiagnostic
from app.db import SessionLocal
from app.routers.membership_admin import _tenant_user_principal
from app.security.tenant import load_authenticated_tenant, require_tenant_headers
from app.services.customer_runtime_service import (
    get_lifecycle,
    lifecycle_access_mode,
    record_connection_diagnostic,
    transition_lifecycle,
    upsert_billing_profile,
)
from app.services.tenant_membership_admin_service import require_tenant_admin

router = APIRouter(tags=["customer-runtime"])


class LifecycleChangeRequest(BaseModel):
    state: str
    reason: str | None = Field(default=None, max_length=255)
    grace_until_utc: datetime | None = None
    pilot_until_utc: datetime | None = None


class BillingProfileRequest(BaseModel):
    legal_company_name: str
    billing_email: str
    address_line1: str
    address_line2: str | None = None
    postal_code: str
    city: str
    region: str | None = None
    country_code: str
    vat_id: str | None = None


class ConnectionDiagnosticRequest(BaseModel):
    environment_name: str | None = None
    company_name: str | None = None
    extension_version: str | None = None
    bc_version: str | None = None
    api_reachable: bool | None = None
    permissions_ok: bool | None = None


@router.get("/account/tenant/lifecycle")
def read_customer_lifecycle(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict:
    _, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        row = get_lifecycle(db, tenant_id)
        db.commit()
        return {
            "tenant_id": tenant_id,
            "state": row.state,
            "access_mode": lifecycle_access_mode(row),
            "effective_from_utc": row.effective_from_utc,
            "grace_until_utc": row.grace_until_utc,
            "pilot_until_utc": row.pilot_until_utc,
            "reason": row.reason,
        }


@router.post("/account/tenant/lifecycle")
def change_customer_lifecycle(
    payload: LifecycleChangeRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        require_tenant_admin(db, user_identity_id=user_id, tenant_id=tenant_id)
        try:
            row = transition_lifecycle(
                db, tenant_id=tenant_id, new_state=payload.state, actor=f"user:{user_id}",
                reason=payload.reason, grace_until_utc=payload.grace_until_utc,
                pilot_until_utc=payload.pilot_until_utc,
            )
            db.commit()
            return {"tenant_id": tenant_id, "state": row.state, "access_mode": lifecycle_access_mode(row)}
        except ValueError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/account/tenant/billing-profile")
def read_billing_profile(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        require_tenant_admin(db, user_identity_id=user_id, tenant_id=tenant_id)
        row = db.get(TenantBillingProfile, tenant_id)
        if row is None:
            return {"tenant_id": tenant_id, "configured": False}
        return {
            "tenant_id": tenant_id, "configured": True, "legal_company_name": row.legal_company_name,
            "billing_email": row.billing_email, "address_line1": row.address_line1,
            "address_line2": row.address_line2, "postal_code": row.postal_code, "city": row.city,
            "region": row.region, "country_code": row.country_code, "vat_id": row.vat_id,
            "tax_treatment": row.tax_treatment,
        }


@router.put("/account/tenant/billing-profile")
def update_billing_profile(
    payload: BillingProfileRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        require_tenant_admin(db, user_identity_id=user_id, tenant_id=tenant_id)
        try:
            row = upsert_billing_profile(db, tenant_id=tenant_id, actor=f"user:{user_id}", **payload.model_dump())
            db.commit()
            return {"tenant_id": tenant_id, "configured": True, "country_code": row.country_code,
                    "tax_treatment": row.tax_treatment}
        except ValueError as exc:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/connection/diagnostics")
def submit_connection_diagnostic(
    payload: ConnectionDiagnosticRequest,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> dict:
    tenant_id, credential = tenant_auth
    with SessionLocal() as db:
        load_authenticated_tenant(db, tenant_id, credential)
        row = record_connection_diagnostic(db, tenant_id=tenant_id, **payload.model_dump())
        db.commit()
        return {"diagnostic_id": row.id, "tenant_id": tenant_id,
                "compatibility_status": row.compatibility_status, "upgrade_required": row.upgrade_required == "true",
                "diagnostic_code": row.diagnostic_code, "message": row.message}


@router.get("/connection/diagnostics/latest")
def latest_connection_diagnostic(
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> dict:
    tenant_id, credential = tenant_auth
    with SessionLocal() as db:
        load_authenticated_tenant(db, tenant_id, credential)
        row = db.scalar(select(TenantConnectionDiagnostic).where(
            TenantConnectionDiagnostic.tenant_id == tenant_id
        ).order_by(TenantConnectionDiagnostic.observed_at_utc.desc(), TenantConnectionDiagnostic.id.desc()).limit(1))
        if row is None:
            return {"tenant_id": tenant_id, "status": "not_run"}
        return {"tenant_id": tenant_id, "status": "available", "environment_name": row.environment_name,
                "company_name": row.company_name, "extension_version": row.extension_version,
                "bc_version": row.bc_version, "compatibility_status": row.compatibility_status,
                "upgrade_required": row.upgrade_required == "true", "diagnostic_code": row.diagnostic_code,
                "message": row.message, "observed_at_utc": row.observed_at_utc}
