from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Scan
from app.security.tenant import load_authenticated_tenant, require_tenant_headers
from app.services.assessment_scope_service import confirm_scope, get_latest_scope, get_or_create_auto_scope, serialize_scope
from app.services.product_license_service import PRODUCT_ASSESSMENT, active_entitlement_product_codes

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


def _has_full_assessment(db, tenant_id: str) -> bool:
    return PRODUCT_ASSESSMENT in active_entitlement_product_codes(db, tenant_id)


@router.get("/{scan_id}/assessment-scope")
def assessment_scope(
    scan_id: str,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> dict:
    tenant_id, api_token = tenant_auth
    with SessionLocal() as db:
        load_authenticated_tenant(db, tenant_id, api_token)
        scan = _load_scan(db, scan_id, tenant_id)
        scope = get_latest_scope(db, scan_id) or get_or_create_auto_scope(db, scan)
        # Free/Quick may use the preliminary score server-side but must not get
        # editable module/check detail. Full Assessment receives the scope UI data.
        return serialize_scope(scope, include_modules=_has_full_assessment(db, tenant_id))


@router.post("/{scan_id}/assessment-scope/confirm")
def confirm_assessment_scope(
    scan_id: str,
    payload: ConfirmScopeRequest,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> dict:
    tenant_id, api_token = tenant_auth
    with SessionLocal() as db:
        load_authenticated_tenant(db, tenant_id, api_token)
        if not _has_full_assessment(db, tenant_id):
            raise HTTPException(status_code=403, detail="Scope confirmation requires an active Full Assessment.")
        scan = _load_scan(db, scan_id, tenant_id)
        scope = confirm_scope(db, scan, payload.decisions)
        return serialize_scope(scope, include_modules=True)
