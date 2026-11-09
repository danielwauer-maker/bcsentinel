"""Scope confirmation creates one immutable baseline from a completed original Free scan."""
from datetime import datetime, timezone

import pytest

from app.core.settings import settings
from app.db import SessionLocal
from app.models import Scan, ScanRunStatus, TenantScanCredit
from app.assessment_scope_models import AssessmentScopeSnapshot


COMPANY = "11111111-2222-3333-4444-555555555555"


@pytest.fixture(autouse=True)
def enable_v2(monkeypatch):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)


def _seed(client, tenant_factory, scan_factory, product_access_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="v2-original-free")
    product_access_factory(tenant_id=tenant["tenant_id"], product_code="full_analysis")
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        scan = db.query(Scan).filter_by(scan_id="v2-original-free").one()
        scan.bc_company_id = COMPANY
        scan.lcy_code = "EUR"
        db.add(ScanRunStatus(
            run_id=scan.scan_id, tenant_id=tenant["tenant_id"], scan_mode="deep",
            status="completed", created_at_utc=now, updated_at_utc=now,
            completed_at_utc=now, result_persisted_at_utc=now,
        ))
        db.add(TenantScanCredit(
            tenant_id=tenant["tenant_id"], product_code="free_entry",
            status="consumed", source="legacy",
            consumed_scan_id=scan.scan_id, created_at_utc=now,
            consumed_at_utc=now,
        ))
        db.commit()
    return tenant


def test_free_baseline_can_be_confirmed_once_and_replayed_without_new_version(
    client, tenant_factory, scan_factory, product_access_factory, auth_header_factory,
):
    tenant = _seed(client, tenant_factory, scan_factory, product_access_factory)
    url = "/scans/v2-original-free/assessment-scope/confirm"
    headers = auth_header_factory(tenant)
    first = client.post(url, headers=headers, json={"decisions": {}})
    assert first.status_code == 200, first.text
    assert first.json()["state"] == "confirmed"
    second = client.post(url, headers=headers, json={"decisions": {}})
    assert second.status_code == 200, second.text
    assert second.json()["version"] == first.json()["version"]
    rejected = client.post(url, headers=headers, json={"decisions": {"finance": "exclude"}})
    assert rejected.status_code == 409
    with SessionLocal() as db:
        assert db.query(AssessmentScopeSnapshot).filter_by(
            scan_id="v2-original-free", state="confirmed"
        ).count() == 1


def test_v2_does_not_confirm_non_free_scans(
    client, tenant_factory, scan_factory, product_access_factory, auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="v2-not-free")
    product_access_factory(tenant_id=tenant["tenant_id"], product_code="full_analysis")
    with SessionLocal() as db:
        scan = db.query(Scan).filter_by(scan_id="v2-not-free").one()
        scan.bc_company_id, scan.lcy_code = COMPANY, "EUR"
        db.commit()
    response = client.post(
        "/scans/v2-not-free/assessment-scope/confirm",
        headers=auth_header_factory(tenant), json={"decisions": {}},
    )
    assert response.status_code == 409
    with SessionLocal() as db:
        assert db.query(AssessmentScopeSnapshot).filter_by(
            scan_id="v2-not-free", state="confirmed"
        ).count() == 0


def test_v2_confirm_rejects_unverified_currency(
    client, tenant_factory, scan_factory, product_access_factory, auth_header_factory,
):
    tenant = _seed(client, tenant_factory, scan_factory, product_access_factory)
    with SessionLocal() as db:
        scan = db.query(Scan).filter_by(scan_id="v2-original-free").one()
        scan.lcy_code = "USD"
        db.commit()
    response = client.post(
        "/scans/v2-original-free/assessment-scope/confirm",
        headers=auth_header_factory(tenant), json={"decisions": {}},
    )
    assert response.status_code == 409
