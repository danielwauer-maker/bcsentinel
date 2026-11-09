from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.core.settings import settings
from app.db import SessionLocal
from app.models import Scan, Tenant
from app.routers.report_legacy_family import _create_share_token, _create_validation_share_token
from app.routers.monitoring_reports import _create_share_token as _create_monitoring_share_token


@pytest.mark.parametrize("family", ["assessment", "validation"])
@pytest.mark.parametrize("format_name", ["html", "pdf"])
def test_v2_legacy_report_rejects_foreign_company_even_with_shared_link(
    client, monkeypatch, tenant_factory, scan_factory, auth_header_factory, family, format_name,
):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    identity = tenant_factory(license_status="active")
    scan_id = f"s3a-{family}-{format_name}"
    scan_factory(tenant_id=identity["tenant_id"], scan_id=scan_id)
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == identity["tenant_id"]))
        tenant.bc_company_id = "11111111-2222-3333-4444-555555555555"
        tenant.premium_until_utc = datetime.now(timezone.utc) + timedelta(days=1)
        scan = db.scalar(select(Scan).where(Scan.scan_id == scan_id))
        scan.bc_company_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        db.commit()
    path = f"/reports/{family}/{scan_id}/{format_name}"
    assert client.get(path, headers=auth_header_factory(identity)).status_code == 404
    create_token = _create_share_token if family == "assessment" else _create_validation_share_token
    token = create_token(tenant_id=identity["tenant_id"], scan_id=scan_id, report_type=format_name)
    assert client.get(path + "/shared", params={"token": token}).status_code == 404


@pytest.mark.parametrize("family", ["assessment", "validation"])
def test_v2_disables_replayable_legacy_premium_links(client, monkeypatch, tenant_factory, family):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    identity = tenant_factory(license_status="active")
    scan_id = "s3a-replayable-link"
    token_factory = _create_share_token if family == "assessment" else _create_validation_share_token
    token = token_factory(tenant_id=identity["tenant_id"], scan_id=scan_id, report_type="pdf")
    path = f"/reports/{family}/{scan_id}/pdf/shared"
    assert client.get(path, params={"token": token}).status_code == 404
    assert client.get(path, params={"token": token}).status_code == 404


def test_v2_disables_replayable_legacy_monitoring_link(client, monkeypatch, tenant_factory):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    identity = tenant_factory(license_status="active")
    token = _create_monitoring_share_token(tenant_id=identity["tenant_id"], scan_id="s3a-monitoring", report_type="pdf")
    path = "/reports/monitoring/s3a-monitoring/pdf/shared"
    assert client.get(path, params={"token": token}).status_code == 404
    assert client.get(path, params={"token": token}).status_code == 404


def test_v2_disables_replayable_executive_share_flow(client, monkeypatch, tenant_factory, auth_header_factory):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    identity = tenant_factory(license_status="active")
    path = "/reports/executive/s3a-executive"
    assert client.post(path + "/share-link", headers=auth_header_factory(identity), json={"report_type": "pdf"}).status_code == 404
    assert client.get(path + "/pdf/shared", params={"token": "test"}).status_code == 404


@pytest.mark.parametrize("family", ["validation", "monitoring"])
@pytest.mark.parametrize("format_name", ["html", "pdf"])
def test_v2_legacy_comparison_export_fails_closed_without_provenance(
    client, monkeypatch, tenant_factory, scan_factory, auth_header_factory, family, format_name,
):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    identity = tenant_factory(license_status="active")
    scan_id = f"s3a-no-provenance-{family}-{format_name}"
    scan_factory(tenant_id=identity["tenant_id"], scan_id=scan_id)
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == identity["tenant_id"]))
        tenant.bc_company_id = "11111111-2222-3333-4444-555555555555"
        tenant.premium_until_utc = datetime.now(timezone.utc) + timedelta(days=1)
        scan = db.scalar(select(Scan).where(Scan.scan_id == scan_id))
        scan.bc_company_id = tenant.bc_company_id
        db.commit()
    response = client.get(f"/reports/{family}/{scan_id}/{format_name}", headers=auth_header_factory(identity))
    assert response.status_code == 409
    assert "comparison evidence" in response.json()["detail"]
