"""Scan-start expectations must be bound at acceptance, never reconstructed."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from threading import Barrier
from uuid import uuid4
from pathlib import Path
import re

import pytest
from sqlalchemy import event, select

from app.db import SessionLocal, engine
from app.models import Scan, ScanExpectationSnapshot, ScanStartRequest, Tenant
from app.services.scan_catalog_contract import catalog_1_0_2_57
from test_product_licensing_p0 import _deep_scan_payload

COMPANY = "11111111-2222-3333-4444-555555555555"
CHECK_A = "CUSTOMERS_MISSING_NAME"
CHECK_B = "CUSTOMERS_MISSING_CITY"


def test_pinned_catalog_matches_current_al_inventory():
    source = (Path(__file__).resolve().parents[2] / "bc-extension/app/src/codeunits/DHScanCheckMgt.Codeunit.al").read_text(encoding="utf-8-sig")
    pairs = re.findall(r"AddCheck\('([^']+)',\s*'([^']+)'", source)
    _, _, catalog = catalog_1_0_2_57()
    assert len(pairs) == 199 and len(set(pairs)) == 199
    assert set(pairs) == catalog


def _request(tenant):
    catalog_version, methodology_version, catalog = catalog_1_0_2_57()
    pairs = [(CHECK_A, "CUSTOMER"), (CHECK_B, "CUSTOMER")]
    pairs += sorted(pair for pair in catalog if pair[0] not in {CHECK_A, CHECK_B})
    return {"tenant_id": tenant["tenant_id"], "run_id": str(uuid4()),
            "client_request_id": str(uuid4()), "scan_mode": "data_health_score", "total_modules": 1,
            "environment_name": "production", "expectation": {
                "schema_version": "bc-scan-expectation-v1", "methodology_version": methodology_version, "catalog_version": catalog_version,
                "company_id": COMPANY, "environment": "production", "currency": "EUR", "modules": ["FINANCE"],
                "checks": [{"code": code, "module": module, "enabled": code == CHECK_A} for code, module in pairs]}}


def _bind(tenant):
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        row.bc_company_id = COMPANY
        row.environment_name = "production"
        db.commit()


def test_start_seals_expectation_and_rejects_changed_or_omitted_retries(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    headers = auth_header_factory(tenant)
    payload = _request(tenant)
    first = client.post("/scan/start", json=payload, headers=headers)
    assert first.status_code == 200, first.text
    with SessionLocal() as db:
        snapshot = db.get(ScanExpectationSnapshot, payload["run_id"])
        assert snapshot and snapshot.tenant_id == tenant["tenant_id"] and snapshot.company_id == COMPANY
        original_hash = snapshot.payload_sha256
    reordered = deepcopy(payload)
    reordered["expectation"]["checks"].reverse()
    assert client.post("/scan/start", json=reordered, headers=headers).status_code == 200
    changed = deepcopy(payload)
    changed["expectation"]["checks"][0]["enabled"] = False
    assert client.post("/scan/start", json=changed, headers=headers).status_code == 409
    omitted = deepcopy(payload)
    del omitted["expectation"]
    assert client.post("/scan/start", json=omitted, headers=headers).status_code == 409
    with SessionLocal() as db:
        assert db.get(ScanExpectationSnapshot, payload["run_id"]).payload_sha256 == original_hash


def test_wrong_company_or_environment_does_not_consume_free_scan(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    headers = auth_header_factory(tenant)
    payload = _request(tenant)
    payload["expectation"]["company_id"] = str(uuid4())
    assert client.post("/scan/start", json=payload, headers=headers).status_code == 409
    payload["expectation"]["company_id"] = COMPANY
    payload["expectation"]["environment"] = "other"
    assert client.post("/scan/start", json=payload, headers=headers).status_code == 409
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        assert row.free_assessment_used is False
        assert db.get(ScanExpectationSnapshot, payload["run_id"]) is None
        assert db.scalar(select(ScanStartRequest).where(ScanStartRequest.scan_id == payload["run_id"])) is None


def test_unregistered_company_cannot_create_verified_expectation(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    payload = _request(tenant)
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        row.bc_company_id = None
        row.environment_name = "production"
        db.commit()
    response = client.post("/scan/start", json=payload, headers=auth_header_factory(tenant))
    assert response.status_code == 409
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        assert row.bc_company_id is None and row.free_assessment_used is False
        assert db.get(ScanExpectationSnapshot, payload["run_id"]) is None


def test_duplicate_checks_do_not_consume_free_scan(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    payload = _request(tenant)
    payload["expectation"]["checks"].append(deepcopy(payload["expectation"]["checks"][0]))
    response = client.post("/scan/start", json=payload, headers=auth_header_factory(tenant))
    assert response.status_code == 422
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        assert row.free_assessment_used is False
        assert db.get(ScanExpectationSnapshot, payload["run_id"]) is None


def test_incomplete_catalog_does_not_consume_free_scan(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    payload = _request(tenant)
    payload["expectation"]["checks"].pop()
    response = client.post("/scan/start", json=payload, headers=auth_header_factory(tenant))
    assert response.status_code == 422
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        assert row.free_assessment_used is False
        assert db.get(ScanExpectationSnapshot, payload["run_id"]) is None


def test_enabled_check_outside_selected_module_is_rejected(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    payload = _request(tenant)
    payload["expectation"]["modules"] = ["SALES"]
    response = client.post("/scan/start", json=payload, headers=auth_header_factory(tenant))
    assert response.status_code == 422
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        assert row.free_assessment_used is False


def test_unrecognized_methodology_does_not_consume_free_scan(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    payload = _request(tenant)
    payload["expectation"]["methodology_version"] = "unsupported-version"
    assert client.post("/scan/start", json=payload, headers=auth_header_factory(tenant)).status_code == 422
    with SessionLocal() as db:
        assert db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"])).free_assessment_used is False


def test_snapshot_persistence_failure_rolls_back_scan_and_free_slot(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    payload = _request(tenant)
    def fail_insert(*_args):
        raise RuntimeError("synthetic snapshot failure")
    event.listen(ScanExpectationSnapshot, "before_insert", fail_insert)
    try:
        with pytest.raises(RuntimeError, match="synthetic snapshot failure"):
            client.post("/scan/start", json=payload, headers=auth_header_factory(tenant))
    finally:
        event.remove(ScanExpectationSnapshot, "before_insert", fail_insert)
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        assert row.free_assessment_used is False
        assert db.get(ScanExpectationSnapshot, payload["run_id"]) is None
        assert db.scalar(select(ScanStartRequest).where(ScanStartRequest.scan_id == payload["run_id"])) is None


def test_legacy_start_cannot_gain_an_expectation_on_retry(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    headers = auth_header_factory(tenant)
    payload = _request(tenant)
    legacy = deepcopy(payload)
    del legacy["expectation"]
    assert client.post("/scan/start", json=legacy, headers=headers).status_code == 200
    assert client.post("/scan/start", json=payload, headers=headers).status_code == 409
    with SessionLocal() as db:
        assert db.get(ScanExpectationSnapshot, payload["run_id"]) is None


def test_existing_orphan_cannot_acquire_new_expectation(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    payload = _request(tenant)
    with SessionLocal() as db:
        db.add(Scan(scan_id=payload["run_id"], tenant_id=tenant["tenant_id"], scan_type="deep",
                    generated_at_utc=datetime.now(timezone.utc), data_score=0, checks_count=0,
                    issues_count=0, premium_available=False, summary_rating="Pending", summary_headline="Pending"))
        db.commit()
    response = client.post("/scan/start", json=payload, headers=auth_header_factory(tenant))
    assert response.status_code == 409
    assert response.json()["code"] == "SCAN_EXPECTATION_REQUIRES_NEW_SCAN"
    with SessionLocal() as db:
        assert db.get(ScanExpectationSnapshot, payload["run_id"]) is None


def test_sync_must_match_sealed_company_currency_scope_and_checks(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    headers = auth_header_factory(tenant)
    start = _request(tenant)
    response = client.post("/scan/start", json=start, headers=headers)
    assert response.status_code == 200, response.text
    payload = _deep_scan_payload(tenant["tenant_id"], start["run_id"])
    payload.update(scan_type="data_health_score", bc_company_id=COMPANY, lcy_code="EUR",
                   enabled_modules=["Finance"], execution_token=response.json()["execution_token"],
                   worker_id=start["client_request_id"])
    payload["issues"][0]["code"] = CHECK_A
    now = datetime.now(timezone.utc).isoformat()
    payload["check_execution_evidence"] = {"schema_version": "bc-check-execution-partial-v1", "checks": [
        {"code": CHECK_A, "status": "FINDINGS", "finding_count": 1, "observed_at_utc": now},
        {"code": CHECK_B, "status": "SKIPPED", "finding_count": 0, "observed_at_utc": now},
    ]}
    for change in (dict(lcy_code="USD"), dict(enabled_modules=["Sales"]), dict(check_execution_evidence=None)):
        bad = deepcopy(payload)
        bad.update(change)
        assert client.post("/scan/sync", json=bad, headers=headers).status_code == 409
    bad = deepcopy(payload)
    bad["check_execution_evidence"]["checks"][1].update(status="PASS")
    assert client.post("/scan/sync", json=bad, headers=headers).status_code == 409
    bad = deepcopy(payload)
    bad["check_execution_evidence"]["checks"][0]["observed_at_utc"] = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    assert client.post("/scan/sync", json=bad, headers=headers).status_code == 409
    response = client.post("/scan/sync", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["execution_evidence_status"] == "partial_stored"


@pytest.mark.skipif(engine.dialect.name != "postgresql", reason="requires PostgreSQL concurrency")
def test_parallel_identical_start_seals_exactly_one_snapshot(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    headers = auth_header_factory(tenant)
    payload = _request(tenant)
    barrier = Barrier(2)
    def submit():
        barrier.wait()
        return client.post("/scan/start", json=payload, headers=headers)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: submit(), range(2)))
    assert [result.status_code for result in results] == [200, 200]
    with SessionLocal() as db:
        assert len(db.scalars(select(ScanExpectationSnapshot).where(ScanExpectationSnapshot.scan_id == payload["run_id"])).all()) == 1


@pytest.mark.skipif(engine.dialect.name != "postgresql", reason="requires PostgreSQL concurrency")
def test_parallel_conflicting_starts_never_replace_snapshot(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    headers = auth_header_factory(tenant)
    first = _request(tenant)
    second = deepcopy(first)
    second["expectation"]["checks"][0]["enabled"] = False
    barrier = Barrier(2)
    def submit(payload):
        barrier.wait()
        return client.post("/scan/start", json=payload, headers=headers)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(submit, (first, second)))
    assert sorted(result.status_code for result in results) == [200, 409]
    with SessionLocal() as db:
        assert len(db.scalars(select(ScanExpectationSnapshot).where(ScanExpectationSnapshot.scan_id == first["run_id"])).all()) == 1
