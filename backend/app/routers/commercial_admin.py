from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.commercial_override_models import TenantCommercialOverride, TenantPilotSponsorship
from app.db import SessionLocal
from app.routers.membership_admin import _tenant_user_principal
from app.services.commercial_checkout_service import commercial_quote
from app.services.tenant_commercial_service import (
    create_commercial_override,
    grant_pilot_sponsorship,
    revoke_commercial_override,
)
from app.services.tenant_membership_admin_service import require_tenant_admin

router = APIRouter(tags=["commercial-admin"])


class CommercialOverrideRequest(BaseModel):
    product_code: str
    override_type: str
    value_number: float = 0.0
    valid_from_utc: datetime
    valid_until_utc: datetime | None = None
    max_uses: int | None = Field(default=None, ge=1)
    reason: str | None = Field(default=None, max_length=255)
    internal_note: str | None = Field(default=None, max_length=2000)


class PilotSponsorshipRequest(BaseModel):
    product_code: str
    valid_from_utc: datetime
    valid_until_utc: datetime
    reason: str = Field(min_length=3, max_length=255)


@router.get("/account/tenant/commercials")
def list_tenant_commercials(authorization: str | None = Header(default=None, alias="Authorization")) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        require_tenant_admin(db, user_identity_id=user_id, tenant_id=tenant_id)
        overrides = db.scalars(select(TenantCommercialOverride).where(
            TenantCommercialOverride.tenant_id == tenant_id
        ).order_by(TenantCommercialOverride.created_at_utc.desc())).all()
        sponsorships = db.scalars(select(TenantPilotSponsorship).where(
            TenantPilotSponsorship.tenant_id == tenant_id
        ).order_by(TenantPilotSponsorship.created_at_utc.desc())).all()
        return {
            "tenant_id": tenant_id,
            "overrides": [{
                "id": row.id, "product_code": row.product_code, "override_type": row.override_type,
                "value_number": row.value_number, "currency": row.currency, "status": row.status,
                "valid_from_utc": row.valid_from_utc, "valid_until_utc": row.valid_until_utc,
                "max_uses": row.max_uses, "uses_count": row.uses_count,
                "reason": row.reason,
            } for row in overrides],
            "pilot_sponsorships": [{
                "id": row.id, "product_code": row.product_code, "status": row.status,
                "valid_from_utc": row.valid_from_utc, "valid_until_utc": row.valid_until_utc,
                "reason": row.reason,
            } for row in sponsorships],
        }


@router.post("/account/tenant/commercial-overrides")
def create_tenant_commercial_override(payload: CommercialOverrideRequest,
                                      authorization: str | None = Header(default=None, alias="Authorization")) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        require_tenant_admin(db, user_identity_id=user_id, tenant_id=tenant_id)
        try:
            row = create_commercial_override(
                db,
                tenant_id=tenant_id,
                product_code=payload.product_code,
                override_type=payload.override_type,
                value_number=payload.value_number,
                valid_from_utc=payload.valid_from_utc,
                valid_until_utc=payload.valid_until_utc,
                max_uses=payload.max_uses,
                reason=payload.reason,
                internal_note=payload.internal_note,
                allow_promotion_code_stack=False,
                actor=f"user:{user_id}",
            )
            db.commit()
            return {"status": "active", "override_id": row.id, "product_code": row.product_code}
        except ValueError as exc:
            db.rollback(); raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.delete("/account/tenant/commercial-overrides/{override_id}")
def revoke_tenant_commercial_override(override_id: int,
                                      authorization: str | None = Header(default=None, alias="Authorization")) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        require_tenant_admin(db, user_identity_id=user_id, tenant_id=tenant_id)
        row = db.get(TenantCommercialOverride, override_id)
        if row is None or row.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Commercial override not found.")
        try:
            revoke_commercial_override(db, override_id=override_id, actor=f"user:{user_id}")
            db.commit(); return {"status": "revoked", "override_id": override_id}
        except ValueError as exc:
            db.rollback(); raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/account/tenant/pilot-sponsorships")
def create_pilot_sponsorship(payload: PilotSponsorshipRequest,
                             authorization: str | None = Header(default=None, alias="Authorization")) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        require_tenant_admin(db, user_identity_id=user_id, tenant_id=tenant_id)
        try:
            row = grant_pilot_sponsorship(
                db,
                tenant_id=tenant_id,
                product_code=payload.product_code,
                valid_from_utc=payload.valid_from_utc,
                valid_until_utc=payload.valid_until_utc,
                actor=f"user:{user_id}",
                reason=payload.reason,
            )
            db.commit()
            return {"status": "active", "sponsorship_id": row.id, "product_code": row.product_code,
                    "valid_until_utc": row.valid_until_utc}
        except ValueError as exc:
            db.rollback(); raise HTTPException(status_code=409, detail=str(exc)) from exc
