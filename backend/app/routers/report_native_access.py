"""BC-native one-time report exchange and tenant-scoped archived Full history."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.core.settings import settings
from app.db import SessionLocal
from app.report_archive_models import ReportArchive
from app.security.tenant import load_authenticated_tenant, require_tenant_headers
from app.services.report_archive_service import redeem_code
from app.services.scan_company_service import canonical_company_id
from app.services.tenant_access_service import enforce_tenant_is_active

router = APIRouter(prefix="/reports/access", tags=["report-access"])


class ExchangeRequest(BaseModel):
    code: str = Field(min_length=32, max_length=256)
    scan_id: str = Field(min_length=1, max_length=50)
    company_id: str = Field(min_length=32, max_length=64)
    report_variant: str = "full"


@router.post("/exchange")
def exchange_report_code(request: ExchangeRequest, response: Response) -> dict:
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["Pragma"] = "no-cache"
    allowed = {"full"}
    if settings.ACCESS_MODEL_V2_ENABLED:
        allowed.update({"validation", "monitoring"})
    if request.report_variant not in allowed:
        raise HTTPException(status_code=403, detail="Report variant not available.")
    with SessionLocal() as db:
        # Atomic one-use exchange. The browser's advertised context must match
        # the grant and the resulting narrowly scoped bearer.
        result = redeem_code(db, request.code)
        try:
            same_company = canonical_company_id(result["company_id"]) == canonical_company_id(request.company_id)
        except ValueError:
            same_company = False
        if (result["scan_id"] != request.scan_id or not same_company
                or result["report_variant"] != request.report_variant):
            raise HTTPException(status_code=403, detail="Report context mismatch.")
        return result


@router.get("/history")
def list_full_report_history(
    response: Response,
    company_id: str = Query(min_length=32, max_length=64),
    limit: int = Query(default=50, ge=1, le=100),
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> dict:
    response.headers["Cache-Control"] = "no-store, private"
    tenant_id, token = tenant_auth
    try:
        company = canonical_company_id(company_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Company not found.") from None
    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, tenant_id, token)
        enforce_tenant_is_active(db, tenant.tenant_id)
        rows = db.scalars(
            select(ReportArchive).where(
                ReportArchive.tenant_id == tenant.tenant_id,
                ReportArchive.company_id == company,
                ReportArchive.variant == "full",
            ).order_by(ReportArchive.created_at_utc.desc()).limit(limit)
        ).all()
        return {"reports": [
            {"scan_id": row.scan_id, "company_id": row.company_id,
             "variant": row.variant, "created_at_utc": row.created_at_utc.isoformat(),
             "sha256": row.sha256}
            for row in rows
        ]}
