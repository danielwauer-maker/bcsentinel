from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

from app.db import SessionLocal
from app.schemas.report import ExecutiveReport
from app.security.tenant import load_authenticated_tenant, require_tenant_headers
from app.services.executive_report_service import build_executive_report, render_executive_report_pdf

router = APIRouter(prefix="/reports", tags=["reports"])
templates = Jinja2Templates(directory="app/templates")


def _load_report(scan_id: str, tenant_auth: tuple[str, str]) -> ExecutiveReport:
    header_tenant_id, header_api_token = tenant_auth
    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, header_tenant_id, header_api_token)
        return build_executive_report(db, tenant, scan_id)


@router.get("/executive/{scan_id}", response_model=ExecutiveReport)
def get_executive_report(
    scan_id: str,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> ExecutiveReport:
    return _load_report(scan_id, tenant_auth)


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
