from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.models import DashboardUser, DashboardUserTenantMembership, Tenant
from app.routers import dashboard, reports
from app.security.token import verify_token


ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_TEMPLATE = ROOT / "backend/app/templates/dashboard_portal.html"


def _route_map(router):
    return {(route.path, method) for route in router.routes for method in getattr(route, "methods", set())}


def test_dashboard_routes_cover_login_logout_tenant_switch_and_embed_token():
    routes = _route_map(dashboard.router)
    expected = {
        ("/dashboard", "GET"),
        ("/dashboard/invite", "GET"),
        ("/dashboard/invite/activate", "POST"),
        ("/dashboard/login", "POST"),
        ("/dashboard/logout", "POST"),
        ("/dashboard/tenants", "GET"),
        ("/dashboard/tenant/{tenant_id}", "GET"),
        ("/dashboard/tenant/switch", "POST"),
        ("/dashboard/analytics-token", "POST"),
    }
    assert expected <= routes


def test_dashboard_session_cookie_is_hardened_and_template_exists():
    source = (ROOT / "backend/app/routers/dashboard.py").read_text(encoding="utf-8")
    assert "httponly=True" in source
    assert 'samesite="strict"' in source
    assert 'secure=settings.ENV.lower() == "prod"' in source
    assert DASHBOARD_TEMPLATE.exists()
    template = DASHBOARD_TEMPLATE.read_text(encoding="utf-8")
    assert "dashboard" in template.lower()
    assert "password" in template.lower()


def test_dashboard_session_token_contains_tenant_and_membership_scope():
    user = DashboardUser(id=11, email="pilot@example.invalid", normalized_email="pilot@example.invalid", status="active")
    membership = DashboardUserTenantMembership(id=22, dashboard_user_id=11, tenant_id="tenant-a", role="owner", is_active=True)
    token = dashboard._session_token(user, membership)
    payload = verify_token(token, audience=dashboard.DASHBOARD_SESSION_AUDIENCE)
    assert payload is not None
    assert payload["type"] == dashboard.DASHBOARD_SESSION_TYPE
    assert payload["scope"] == "dashboard:user"
    assert payload["user_id"] == 11
    assert payload["membership_id"] == 22
    assert payload["active_tenant_id"] == "tenant-a"
    assert payload["role"] == "owner"


def test_report_routes_cover_json_html_pdf_and_time_limited_share_links():
    routes = _route_map(reports.router)
    expected = {
        ("/reports/executive/{scan_id}", "GET"),
        ("/reports/executive/{scan_id}/share-link", "POST"),
        ("/reports/executive/{scan_id}/html", "GET"),
        ("/reports/executive/{scan_id}/html/shared", "GET"),
        ("/reports/executive/{scan_id}/pdf", "GET"),
        ("/reports/executive/{scan_id}/pdf/shared", "GET"),
    }
    assert expected <= routes
    assert reports.REPORT_SHARE_TOKEN_MINUTES <= 15
    assert reports.REPORT_SHARE_ALGORITHM == "HS256"


def test_report_share_token_is_bound_to_tenant_company_scan_type_and_capability():
    tenant = Tenant(
        tenant_id="tenant-a",
        environment_name="Sandbox",
        bc_company_id="company-a",
        bc_company_name="Pilot GmbH",
    )
    token = reports._create_share_token(tenant=tenant, scan_id="scan-123", report_type="pdf")
    tenant_id, scan_id, company_id = reports._verify_share_token(token, scan_id="scan-123", report_type="pdf")
    assert tenant_id == "tenant-a"
    assert scan_id == "scan-123"
    assert company_id == "company-a"

    with pytest.raises(HTTPException) as wrong_scan:
        reports._verify_share_token(token, scan_id="scan-other", report_type="pdf")
    assert wrong_scan.value.status_code == 403

    with pytest.raises(HTTPException) as wrong_type:
        reports._verify_share_token(token, scan_id="scan-123", report_type="html")
    assert wrong_type.value.status_code == 403


def test_pdf_response_declares_pdf_media_type_and_safe_filename_contract():
    source = (ROOT / "backend/app/routers/reports.py").read_text(encoding="utf-8")
    assert 'media_type="application/pdf"' in source
    assert 'filename="bcsentinel-executive-report-{scan_id}.pdf"' in source
    assert "require_capability(db, tenant, CAPABILITY_REPORT" in source
