"""The report preflight must be read-only and tenant authenticated."""
from app.db import SessionLocal
from app.models import Scan
from app.assessment_scope_models import AssessmentScopeSnapshot


def test_report_preflight_returns_missing_evidence_without_creating_scope(
    client, tenant_factory, scan_factory, auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="preflight-missing")
    response = client.get(
        "/scans/preflight-missing/report-preflight",
        headers=auth_header_factory(tenant),
    )
    assert response.status_code == 200, response.text
    info = response.json()
    assert info["preflight_only"] is True
    assert info["scope_state"] == "missing"
    assert info["confirmed_scope_version"] is None
    assert info["company_bound"] is False
    assert info["validation_comparison"] is None
    assert "scope_snapshot_missing" in info["missing_prerequisites"]
    with SessionLocal() as db:
        assert db.query(AssessmentScopeSnapshot).filter_by(scan_id="preflight-missing").count() == 0


def test_report_preflight_denies_foreign_tenant(
    client, tenant_factory, scan_factory, auth_header_factory,
):
    owner = tenant_factory()
    other = tenant_factory()
    scan_factory(tenant_id=owner["tenant_id"], scan_id="preflight-foreign")
    response = client.get(
        "/scans/preflight-foreign/report-preflight",
        headers=auth_header_factory(other),
    )
    assert response.status_code == 403


def test_v2_preflight_requires_original_completed_free_scan(
    client, tenant_factory, scan_factory, auth_header_factory, monkeypatch,
):
    from app.core.settings import settings
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="preflight-unverified-free")
    response = client.get(
        "/scans/preflight-unverified-free/report-preflight",
        headers=auth_header_factory(tenant),
    )
    assert response.status_code == 200, response.text
    info = response.json()
    assert info["original_free_scan"] is False
    assert "original_completed_free_scan_missing" in info["missing_prerequisites"]
