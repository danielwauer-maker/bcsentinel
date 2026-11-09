from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import select

from app.core.settings import resolve_public_base_url, settings
from app.db import SessionLocal
from app.models import Scan, Tenant
from app.schemas.monitoring_report import MonitoringReport
from app.security.tenant import load_authenticated_tenant, require_tenant_headers
from app.services.monitoring_report_pdf_service import render_monitoring_report_pdf
from app.services.monitoring_report_service import build_monitoring_report
from app.services.tenant_access_service import enforce_tenant_is_active

router = APIRouter(prefix="/monitoring", tags=["reports"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
MONITORING_REPORT_SHARE_TOKEN_TYPE = "monitoring_report_share"
REPORT_SHARE_TOKEN_MINUTES = 15
REPORT_SHARE_ALGORITHM = "HS256"


class MonitoringReportShareLinkRequest(BaseModel):
    report_type: str = "html"


class MonitoringReportShareLinkResponse(BaseModel):
    url: str


def _require_owned_scan(db, tenant_id: str, scan_id: str) -> None:
    owned = db.scalar(select(Scan.id).where(Scan.tenant_id == tenant_id, Scan.scan_id == scan_id))
    if owned is None:
        raise HTTPException(status_code=404, detail="Monitoring report scan not found.")


def _load_report(scan_id: str, tenant_auth: tuple[str, str]) -> MonitoringReport:
    tenant_id, api_token = tenant_auth
    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, tenant_id, api_token)
        _require_owned_scan(db, tenant.tenant_id, scan_id)
        return build_monitoring_report(db, tenant, scan_id)


def _create_share_token(*, tenant_id: str, scan_id: str, report_type: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=REPORT_SHARE_TOKEN_MINUTES)
    payload = {
        "type": MONITORING_REPORT_SHARE_TOKEN_TYPE,
        "tenant_id": tenant_id,
        "scan_id": scan_id,
        "report_type": report_type,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=REPORT_SHARE_ALGORITHM)


def _verify_share_token(token: str, *, scan_id: str, report_type: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[REPORT_SHARE_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired Monitoring report share token.")
    tenant_id = str(payload.get("tenant_id") or "")
    if (
        str(payload.get("type") or "") != MONITORING_REPORT_SHARE_TOKEN_TYPE
        or not tenant_id
        or str(payload.get("scan_id") or "") != scan_id
        or str(payload.get("report_type") or "") != report_type
    ):
        raise HTTPException(status_code=403, detail="Invalid Monitoring report share token.")
    return tenant_id


def _load_shared_report(scan_id: str, report_type: str, token: str) -> MonitoringReport:
    if settings.ACCESS_MODEL_V2_ENABLED:
        raise HTTPException(status_code=404, detail="Use the single-use report access flow.")
    tenant_id = _verify_share_token(token, scan_id=scan_id, report_type=report_type)
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
        if tenant is None:
            raise HTTPException(status_code=403, detail="Invalid Monitoring report share token.")
        enforce_tenant_is_active(db, tenant.tenant_id)
        _require_owned_scan(db, tenant.tenant_id, scan_id)
        return build_monitoring_report(db, tenant, scan_id)


def _shared_url(request: Request, scan_id: str, report_type: str, token: str) -> str:
    base_url = resolve_public_base_url() or str(request.base_url).rstrip("/")
    return f"{base_url}/reports/monitoring/{quote(scan_id)}/{report_type}/shared?token={quote(token)}"


@router.get("/{scan_id}", response_model=MonitoringReport)
def get_monitoring_report(scan_id: str, tenant_auth: tuple[str, str] = Depends(require_tenant_headers)) -> MonitoringReport:
    return _load_report(scan_id, tenant_auth)


@router.post("/{scan_id}/share-link", response_model=MonitoringReportShareLinkResponse)
def create_monitoring_report_share_link(
    request: Request,
    scan_id: str,
    payload: MonitoringReportShareLinkRequest | None = None,
    report_type: str | None = Query(default=None),
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> MonitoringReportShareLinkResponse:
    if settings.ACCESS_MODEL_V2_ENABLED:
        raise HTTPException(status_code=404, detail="Use the single-use report access flow.")
    selected_type = (report_type or (payload.report_type if payload else "html") or "html").strip().lower()
    if selected_type not in {"html", "pdf"}:
        raise HTTPException(status_code=400, detail="report_type must be html or pdf.")
    _load_report(scan_id, tenant_auth)
    token = _create_share_token(tenant_id=tenant_auth[0], scan_id=scan_id, report_type=selected_type)
    return MonitoringReportShareLinkResponse(url=_shared_url(request, scan_id, selected_type, token))


@router.get("/{scan_id}/html", response_class=HTMLResponse)
def render_monitoring_report_html(
    request: Request,
    scan_id: str,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    report = _load_report(scan_id, tenant_auth)
    return templates.TemplateResponse(name="monitoring_report.html", context={"request": request, "report": report})


@router.get("/{scan_id}/html/shared", response_class=HTMLResponse)
def render_shared_monitoring_report_html(request: Request, scan_id: str, token: str):
    report = _load_shared_report(scan_id, "html", token)
    return templates.TemplateResponse(name="monitoring_report.html", context={"request": request, "report": report})


@router.get("/{scan_id}/pdf")
def export_monitoring_report_pdf(
    scan_id: str,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    report = _load_report(scan_id, tenant_auth)
    pdf_bytes = render_monitoring_report_pdf(report)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="bcsentinel-monitoring-report-{scan_id}.pdf"'},
    )


@router.get("/{scan_id}/pdf/shared")
def export_shared_monitoring_report_pdf(scan_id: str, token: str):
    report = _load_shared_report(scan_id, "pdf", token)
    pdf_bytes = render_monitoring_report_pdf(report)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="bcsentinel-monitoring-report-{scan_id}.pdf"'},
    )
