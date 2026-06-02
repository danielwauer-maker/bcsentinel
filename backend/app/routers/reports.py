from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

from jose import JWTError, jwt
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from app.core.settings import settings
from app.db import SessionLocal
from app.models import Tenant
from app.schemas.report import ExecutiveReport
from app.security.tenant import load_authenticated_tenant, require_tenant_headers
from app.services.executive_report_service import build_executive_report, render_executive_report_pdf
from app.services.product_license_service import build_product_access_snapshot

router = APIRouter(prefix="/reports", tags=["reports"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
REPORT_SHARE_TOKEN_TYPE = "executive_report_share"
REPORT_SHARE_TOKEN_MINUTES = 15
REPORT_SHARE_ALGORITHM = "HS256"


class ExecutiveReportShareLinkRequest(BaseModel):
    report_type: str = "html"


class ExecutiveReportShareLinkResponse(BaseModel):
    url: str


def _load_report(scan_id: str, tenant_auth: tuple[str, str]) -> ExecutiveReport:
    header_tenant_id, header_api_token = tenant_auth
    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, header_tenant_id, header_api_token)
        report = build_executive_report(db, tenant, scan_id)
        access = build_product_access_snapshot(db, tenant)
        if not access["can_view_executive_report"]:
            raise HTTPException(
                status_code=402,
                detail="Executive Report access requires an active Assessment, Validation Check, or Monitoring subscription.",
            )
        return report


def _create_share_token(*, tenant_id: str, scan_id: str, report_type: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=REPORT_SHARE_TOKEN_MINUTES)
    payload = {
        "type": REPORT_SHARE_TOKEN_TYPE,
        "tenant_id": tenant_id,
        "scan_id": scan_id,
        "report_type": report_type,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=REPORT_SHARE_ALGORITHM)


def _verify_share_token(token: str, *, scan_id: str, report_type: str) -> tuple[str, str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[REPORT_SHARE_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired report share token.")

    tenant_id = str(payload.get("tenant_id") or "")
    token_scan_id = str(payload.get("scan_id") or "")
    token_report_type = str(payload.get("report_type") or "")
    token_type = str(payload.get("type") or "")
    if (
        token_type != REPORT_SHARE_TOKEN_TYPE
        or not tenant_id
        or token_scan_id != scan_id
        or token_report_type != report_type
    ):
        raise HTTPException(status_code=403, detail="Invalid report share token.")

    return tenant_id, token_scan_id


def _load_shared_report(scan_id: str, report_type: str, token: str) -> ExecutiveReport:
    tenant_id, _ = _verify_share_token(token, scan_id=scan_id, report_type=report_type)
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
        if tenant is None:
            raise HTTPException(status_code=403, detail="Invalid report share token.")
        report = build_executive_report(db, tenant, scan_id)
        access = build_product_access_snapshot(db, tenant)
        if not access["can_view_executive_report"]:
            raise HTTPException(status_code=403, detail="Report access is no longer active.")
        return report


def _shared_report_url(request: Request, scan_id: str, report_type: str, token: str) -> str:
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}/reports/executive/{quote(scan_id)}/{report_type}/shared?token={quote(token)}"


@router.get("/executive/{scan_id}", response_model=ExecutiveReport)
def get_executive_report(
    scan_id: str,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> ExecutiveReport:
    return _load_report(scan_id, tenant_auth)


@router.post("/executive/{scan_id}/share-link", response_model=ExecutiveReportShareLinkResponse)
def create_executive_report_share_link(
    request: Request,
    scan_id: str,
    payload: ExecutiveReportShareLinkRequest | None = None,
    report_type: str | None = Query(default=None),
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> ExecutiveReportShareLinkResponse:
    selected_type = (report_type or (payload.report_type if payload else "html") or "html").strip().lower()
    if selected_type not in {"html", "pdf"}:
        raise HTTPException(status_code=400, detail="report_type must be html or pdf.")

    header_tenant_id, header_api_token = tenant_auth
    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, header_tenant_id, header_api_token)
        build_executive_report(db, tenant, scan_id)
        access = build_product_access_snapshot(db, tenant)
        if not access["can_view_executive_report"]:
            raise HTTPException(
                status_code=402,
                detail="Executive Report access requires an active Assessment, Validation Check, or Monitoring subscription.",
            )

    token = _create_share_token(
        tenant_id=header_tenant_id,
        scan_id=scan_id,
        report_type=selected_type,
    )
    return ExecutiveReportShareLinkResponse(
        url=_shared_report_url(request, scan_id, selected_type, token)
    )


@router.get("/executive/{scan_id}/html", response_class=HTMLResponse)
def render_executive_report_html(
    request: Request,
    scan_id: str,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    report = _load_report(scan_id, tenant_auth)
    return templates.TemplateResponse(
        name="executive_report.html",
        context={"request": request, "report": report},
    )


@router.get("/executive/{scan_id}/html/shared", response_class=HTMLResponse)
def render_shared_executive_report_html(
    request: Request,
    scan_id: str,
    token: str,
):
    report = _load_shared_report(scan_id, "html", token)
    return templates.TemplateResponse(
        name="executive_report.html",
        context={"request": request, "report": report},
    )


@router.get("/executive/{scan_id}/pdf")
def export_executive_report_pdf(
    scan_id: str,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    report = _load_report(scan_id, tenant_auth)
    pdf_bytes = render_executive_report_pdf(report)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="bcsentinel-executive-report-{scan_id}.pdf"'},
    )


@router.get("/executive/{scan_id}/pdf/shared")
def export_shared_executive_report_pdf(
    scan_id: str,
    token: str,
):
    report = _load_shared_report(scan_id, "pdf", token)
    pdf_bytes = render_executive_report_pdf(report)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="bcsentinel-executive-report-{scan_id}.pdf"'},
    )
