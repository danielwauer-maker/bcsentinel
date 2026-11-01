from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Scan
from app.security.tenant import load_authenticated_tenant, require_tenant_headers
from app.services.report_access_service import resolve_preferred_report_variant

router = APIRouter(prefix="/reports", tags=["reports"])


class PreferredReportVariantResponse(BaseModel):
    scan_id: str
    report_variant: str


@router.get("/{scan_id}/preferred-variant", response_model=PreferredReportVariantResponse)
def get_preferred_report_variant(
    scan_id: str,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> PreferredReportVariantResponse:
    header_tenant_id, header_api_token = tenant_auth
    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, header_tenant_id, header_api_token)
        owned_scan = db.scalar(
            select(Scan.id).where(Scan.scan_id == scan_id, Scan.tenant_id == tenant.tenant_id)
        )
        if owned_scan is None:
            raise HTTPException(status_code=404, detail="Report not found.")
        return PreferredReportVariantResponse(
            scan_id=scan_id,
            report_variant=resolve_preferred_report_variant(db, tenant, scan_id=scan_id),
        )
