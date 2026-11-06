"""V6 navigation links carry no access credentials and never bypass account auth."""
from __future__ import annotations

from app.core.settings import settings
from app.db import SessionLocal
from app.models import Scan
from app.routers import reports

COMPANY = "11111111-2222-3333-4444-555555555555"
OTHER_COMPANY = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def _scan(tenant_factory, scan_factory):
    tenant = tenant_factory()
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="v6_navigation_scan")
    with SessionLocal() as db:
        row = db.query(Scan).filter(Scan.scan_id == "v6_navigation_scan").one()
        row.bc_company_id = COMPANY
        row.lcy_code = "EUR"
        db.commit()
    return tenant


def _url():
    return "/reports/executive/v6_navigation_scan/v6-link"


def test_v6_launch_not_enabled_by_default(client, tenant_factory, scan_factory, auth_header_factory):
    tenant = _scan(tenant_factory, scan_factory)
    res = client.post(_url(), headers=auth_header_factory(tenant))
    assert res.status_code == 503


def test_v6_launch_rejects_unauthenticated(client, monkeypatch):
    monkeypatch.setattr(settings, "REPORT_V6_VIEWER_BASE_URL", "https://example.com")
    assert client.post(_url()).status_code in (401, 403)


def test_v6_launch_returns_only_navigation_context(client, monkeypatch, tenant_factory, scan_factory, auth_header_factory):
    tenant = _scan(tenant_factory, scan_factory)
    monkeypatch.setattr(settings, "REPORT_V6_VIEWER_BASE_URL", "https://reports.example.test")
    monkeypatch.setattr(reports, "build_product_access_snapshot", lambda db, tenant: {
        "can_view_executive_report": True, "assessment_access_active": True
    })
    res = client.post(_url(), headers=auth_header_factory(tenant))
    assert res.status_code == 200, res.text
    result = res.json()["url"]
    assert result.startswith("https://reports.example.test/report/live?")
    assert "scanId=v6_navigation_scan" in result
    assert "companyId=" in result
    assert tenant["api_token"] not in result
    assert tenant["tenant_id"] not in result
    assert "Bearer" not in result
    assert "token" not in result.lower()


def test_v6_launch_requires_paid_full_access(client, monkeypatch, tenant_factory, scan_factory, auth_header_factory):
    tenant = _scan(tenant_factory, scan_factory)
    monkeypatch.setattr(settings, "REPORT_V6_VIEWER_BASE_URL", "https://reports.example.test")
    monkeypatch.setattr(reports, "build_product_access_snapshot", lambda db, tenant: {
        "can_view_executive_report": True, "assessment_access_active": False,
        "monitoring_active": False
    })
    assert client.post(_url(), headers=auth_header_factory(tenant)).status_code == 402


def test_v6_launch_unknown_scan_or_wrong_tenant(client, monkeypatch, tenant_factory, scan_factory, auth_header_factory):
    _scan(tenant_factory, scan_factory)
    second_tenant = tenant_factory()
    monkeypatch.setattr(settings, "REPORT_V6_VIEWER_BASE_URL", "https://reports.example.test")
    assert client.post(_url(), headers=auth_header_factory(second_tenant)).status_code == 404


def test_v6_launch_rejects_non_https_viewer(client, monkeypatch, tenant_factory, scan_factory, auth_header_factory):
    tenant = _scan(tenant_factory, scan_factory)
    for bad_url in ("http://reports.example.test", "https://user:secret@reports.example.test", "https://reports.example.test?token=abc"):
        monkeypatch.setattr(settings, "REPORT_V6_VIEWER_BASE_URL", bad_url)
        assert client.post(_url(), headers=auth_header_factory(tenant)).status_code == 503
