from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Scan, Tenant
from app.routers.membership_admin import _tenant_user_principal
from app.security.tenant import load_authenticated_tenant
from app.services.assessment_scope_service import confirm_scope, get_latest_scope, get_or_create_auto_scope, serialize_scope
from app.services.entitlement_guard_service import get_tenant_features

router = APIRouter(prefix="/scans", tags=["assessment-scope"])


class ConfirmScopeRequest(BaseModel):
    decisions: dict[str, str] = Field(default_factory=dict)


def _load_scan(db, scan_id: str, tenant_id: str) -> Scan:
    scan = db.scalar(select(Scan).where(Scan.scan_id == scan_id))
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found.")
    if scan.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Scan does not belong to authenticated tenant.")
    return scan


def _resolve_tenant(
    db,
    *,
    authorization: str | None,
    tenant_id_header: str | None,
    api_token_header: str | None,
) -> Tenant:
    if authorization:
        _, tenant_id, _ = _tenant_user_principal(authorization)
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
        if tenant is None:
            raise HTTPException(status_code=404, detail="Tenant not found.")
        return tenant

    if tenant_id_header and api_token_header:
        return load_authenticated_tenant(db, tenant_id_header, api_token_header)

    raise HTTPException(status_code=401, detail="Tenant authentication required.")


def _has_full_assessment(db, tenant: Tenant) -> bool:
    # Channel-neutral feature resolution: direct purchase, Fiverr/operator grant
    # and compatible paid access all expose the same Full Assessment capability.
    return "executive_report" in get_tenant_features(db, tenant)


@router.get("/{scan_id}/assessment-scope")
def assessment_scope(
    scan_id: str,
    authorization: str | None = Header(default=None, alias="Authorization"),
    tenant_id_header: str | None = Header(default=None, alias="X-Tenant-Id"),
    api_token_header: str | None = Header(default=None, alias="X-Api-Token"),
) -> dict:
    with SessionLocal() as db:
        tenant = _resolve_tenant(
            db,
            authorization=authorization,
            tenant_id_header=tenant_id_header,
            api_token_header=api_token_header,
        )
        scan = _load_scan(db, scan_id, tenant.tenant_id)
        scope = get_latest_scope(db, scan_id) or get_or_create_auto_scope(db, scan)
        # Free/Quick may consume the scope summary but never receive module-level
        # edit data. Full Assessment receives the module list for confirmation.
        return serialize_scope(scope, include_modules=_has_full_assessment(db, tenant))


@router.post("/{scan_id}/assessment-scope/confirm")
def confirm_assessment_scope(
    scan_id: str,
    payload: ConfirmScopeRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
    tenant_id_header: str | None = Header(default=None, alias="X-Tenant-Id"),
    api_token_header: str | None = Header(default=None, alias="X-Api-Token"),
) -> dict:
    with SessionLocal() as db:
        tenant = _resolve_tenant(
            db,
            authorization=authorization,
            tenant_id_header=tenant_id_header,
            api_token_header=api_token_header,
        )
        if not _has_full_assessment(db, tenant):
            raise HTTPException(status_code=403, detail="Scope confirmation requires an active Full Assessment.")
        scan = _load_scan(db, scan_id, tenant.tenant_id)
        scope = confirm_scope(db, scan, payload.decisions)
        return serialize_scope(scope, include_modules=True)
