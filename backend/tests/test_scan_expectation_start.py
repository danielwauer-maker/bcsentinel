"""Scan-start expectations must be bound at acceptance, never reconstructed."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from threading import Barrier
from uuid import uuid4
from pathlib import Path
import re

import pytest
from sqlalchemy import event, select

from app.db import SessionLocal, engine
from app.models import Scan, ScanExecutionEvidence, ScanExpectationSnapshot, ScanRunStatus, ScanStartRequest, Tenant
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


def test_capability_preflight_authentication_and_company_binding(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    headers = auth_header_factory(tenant)
    assert client.get("/scan/expectation-capabilities").status_code in {401, 403, 422}
    unbound = client.get("/scan/expectation-capabilities", headers=headers)
    assert unbound.status_code == 200
    assert unbound.json()["expectation_status"] == "unavailable_company_binding"
    _bind(tenant)
    response = client.get("/scan/expectation-capabilities", headers=headers)
    assert response.status_code == 200 and response.json()["expectation_status"] == "supported"
    bad_headers = dict(headers, **{"X-Api-Token": "invalid-token"})
    assert client.get("/scan/expectation-capabilities", headers=bad_headers).status_code in {401, 403}
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        assert row.free_assessment_used is False


def test_start_seals_expectation_and_rejects_changed_or_omitted_retries(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    headers = auth_header_factory(tenant)
    payload = _request(tenant)
    first = client.post("/scan/start", json=payload, headers=headers)
    assert first.status_code == 200, first.text
    assert first.json()["expectation_status"] == "accepted"
    with SessionLocal() as db:
        snapshot = db.get(ScanExpectationSnapshot, payload["run_id"])
        assert snapshot and snapshot.tenant_id == tenant["tenant_id"] and snapshot.company_id == COMPANY
        assert "exception_scope" not in json.loads(snapshot.payload_json)
        original_hash = snapshot.payload_sha256
    reordered = deepcopy(payload)
    reordered["expectation"]["checks"].reverse()
    retry = client.post("/scan/start", json=reordered, headers=headers)
    assert retry.status_code == 200 and retry.json()["expectation_status"] == "accepted"
    changed = deepcopy(payload)
    changed["expectation"]["checks"][1]["enabled"] = True
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


def test_frozen_al_10258_methodology_is_accepted(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    payload = _request(tenant)
    payload["expectation"]["methodology_version"] = "bc-deep-scan-1.0.2.58"
    response = client.post("/scan/start", json=payload, headers=auth_header_factory(tenant))
    assert response.status_code == 200, response.text
    assert response.json()["expectation_status"] == "accepted"


def test_v2_exception_scope_is_frozen_and_order_independent(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    headers = auth_header_factory(tenant)
    payload = _request(tenant)
    payload["expectation"].update(schema_version="bc-scan-expectation-v2", methodology_version="bc-deep-scan-1.0.2.58",
        exception_scope=[{"entry_no": 2, "table_id": 18, "record_system_id": str(uuid4()), "issue_code": CHECK_A},
                         {"entry_no": 1, "table_id": 18, "record_system_id": str(uuid4()), "issue_code": CHECK_B}])
    response = client.post("/scan/start", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    with SessionLocal() as db:
        data = json.loads(db.get(ScanExpectationSnapshot, payload["run_id"]).payload_json)
        assert [item["entry_no"] for item in data["exception_scope"]] == [1, 2]
    retry = deepcopy(payload)
    retry["expectation"]["exception_scope"].reverse()
    assert client.post("/scan/start", json=retry, headers=headers).status_code == 200
    retry["expectation"]["exception_scope"][0]["issue_code"] = CHECK_A
    assert client.post("/scan/start", json=retry, headers=headers).status_code == 409


def test_v2_missing_exception_scope_is_rejected_without_free_consumption(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    payload = _request(tenant)
    payload["expectation"]["schema_version"] = "bc-scan-expectation-v2"
    assert client.post("/scan/start", json=payload, headers=auth_header_factory(tenant)).status_code == 422
    with SessionLocal() as db:
        assert db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"])).free_assessment_used is False


def test_no_enabled_checks_does_not_consume_free_scan(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    payload = _request(tenant)
    for check in payload["expectation"]["checks"]:
        check["enabled"] = False
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


def test_result_and_completion_roll_back_together_on_interruption(client, tenant_factory, auth_header_factory, monkeypatch):
    from app.routers import scans as scan_router
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    headers = auth_header_factory(tenant)
    start = _request(tenant)
    accepted = client.post("/scan/start", json=start, headers=headers)
    assert accepted.status_code == 200
    payload = _deep_scan_payload(tenant["tenant_id"], start["run_id"])
    payload.update(scan_type="data_health_score", bc_company_id=COMPANY, lcy_code="EUR", enabled_modules=["Finance"],
                   execution_token=accepted.json()["execution_token"], worker_id=start["client_request_id"])
    payload["issues"][0]["code"] = CHECK_A
    now = datetime.now(timezone.utc).isoformat()
    payload["check_execution_evidence"] = {"schema_version": "bc-check-execution-partial-v1", "checks": [
        {"code": CHECK_A, "status": "FINDINGS", "finding_count": 1, "observed_at_utc": now}]}
    original = scan_router.update_scan_progress
    def interrupt_after_persistence(db, **kwargs):
        if kwargs.get("status") == "completed":
            raise RuntimeError("synthetic interruption before completion")
        return original(db, **kwargs)
    monkeypatch.setattr(scan_router, "update_scan_progress", interrupt_after_persistence)
    with pytest.raises(RuntimeError, match="synthetic interruption"):
        client.post("/scan/sync", json=payload, headers=headers)
    with SessionLocal() as db:
        run = db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == start["run_id"]))
        assert run.status == "queued" and run.result_persisted_at_utc is None
        assert db.get(ScanExecutionEvidence, start["run_id"]) is None
        assert db.get(ScanExpectationSnapshot, start["run_id"]) is not None
    monkeypatch.setattr(scan_router, "update_scan_progress", original)
    response = client.post("/scan/sync", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["scan_status"]["status"] == "completed"


def test_missing_expected_check_cannot_finalize_scan(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    headers = auth_header_factory(tenant)
    start = _request(tenant)
    start["expectation"]["checks"][1]["enabled"] = True
    accepted = client.post("/scan/start", json=start, headers=headers)
    assert accepted.status_code == 200
    payload = _deep_scan_payload(tenant["tenant_id"], start["run_id"])
    payload.update(scan_type="data_health_score", bc_company_id=COMPANY, lcy_code="EUR", enabled_modules=["Finance"],
                   execution_token=accepted.json()["execution_token"], worker_id=start["client_request_id"])
    payload["issues"][0]["code"] = CHECK_A
    now = datetime.now(timezone.utc).isoformat()
    payload["check_execution_evidence"] = {"schema_version": "bc-check-execution-partial-v1", "checks": [
        {"code": CHECK_A, "status": "FINDINGS", "finding_count": 1, "observed_at_utc": now}]}
    assert client.post("/scan/sync", json=payload, headers=headers).status_code == 409
    with SessionLocal() as db:
        run = db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == start["run_id"]))
        assert run.status == "queued" and run.result_persisted_at_utc is None
        assert db.get(ScanExecutionEvidence, start["run_id"]) is None
    payload["check_execution_evidence"]["checks"].append(
        {"code": CHECK_B, "status": "PASS", "finding_count": 0, "observed_at_utc": now})
    response = client.post("/scan/sync", json=payload, headers=headers)
    assert response.status_code == 200, response.text


def test_failed_scan_evidence_is_atomic_and_replay_safe(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    headers = auth_header_factory(tenant)
    start = _request(tenant)
    accepted = client.post("/scan/start", json=start, headers=headers)
    assert accepted.status_code == 200, accepted.text
    status = {"tenant_id": tenant["tenant_id"], "run_id": start["run_id"], "scan_mode": "data_health_score",
              "status": "running", "execution_token": accepted.json()["execution_token"],
              "worker_id": start["client_request_id"]}
    running = client.post("/scan/status/update", json=status, headers=headers)
    assert running.status_code == 200, running.text
    now = datetime.now(timezone.utc).isoformat()
    failed = dict(status, status="failed", failure_evidence={"schema_version": "bc-check-failure-partial-v1", "checks": [
        {"code": CHECK_A, "status": "FAILED", "finding_count": 1, "observed_at_utc": now},
        {"code": CHECK_B, "status": "SKIPPED", "finding_count": 0, "observed_at_utc": now},
    ]})
    with SessionLocal() as db:
        db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"])).bc_company_id = str(uuid4())
        db.commit()
    assert client.post("/scan/status/update", json=failed, headers=headers).status_code == 409
    _bind(tenant)
    wrong = deepcopy(failed)
    wrong["failure_evidence"]["checks"][1]["status"] = "FAILED"
    assert client.post("/scan/status/update", json=wrong, headers=headers).status_code == 409
    with SessionLocal() as db:
        assert db.get(ScanExecutionEvidence, start["run_id"]) is None
    response = client.post("/scan/status/update", json=failed, headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "failed"
    with SessionLocal() as db:
        evidence = db.get(ScanExecutionEvidence, start["run_id"])
        assert evidence and evidence.schema_version == "bc-check-failure-partial-v1"
    assert client.post("/scan/status/update", json=failed, headers=headers).status_code == 200
    altered = deepcopy(failed)
    altered["failure_evidence"]["checks"][0]["finding_count"] = 2
    assert client.post("/scan/status/update", json=altered, headers=headers).status_code == 409
    omitted = dict(failed)
    omitted.pop("failure_evidence")
    assert client.post("/scan/status/update", json=omitted, headers=headers).status_code == 409
    wrong_token = dict(failed, execution_token=str(uuid4()))
    assert client.post("/scan/status/update", json=wrong_token, headers=headers).status_code == 409
    # Metadata-created test databases omit migration triggers: simulate an
    # independently corrupted row and ensure the stored payload is rehashed.
    with SessionLocal() as db:
        db.get(ScanExecutionEvidence, start["run_id"]).payload_json = "{}"
        db.commit()
    assert client.post("/scan/status/update", json=failed, headers=headers).status_code == 409


def test_failed_evidence_storage_error_rolls_back_terminal_status(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    headers = auth_header_factory(tenant)
    start = _request(tenant)
    accepted = client.post("/scan/start", json=start, headers=headers)
    assert accepted.status_code == 200
    base = {"tenant_id": tenant["tenant_id"], "run_id": start["run_id"], "scan_mode": "data_health_score",
            "status": "running", "execution_token": accepted.json()["execution_token"],
            "worker_id": start["client_request_id"]}
    assert client.post("/scan/status/update", json=base, headers=headers).status_code == 200
    failed = dict(base, status="failed", failure_evidence={"schema_version": "bc-check-failure-partial-v1", "checks": []})
    def fail_insert(*_args):
        raise RuntimeError("synthetic failure evidence error")
    event.listen(ScanExecutionEvidence, "before_insert", fail_insert)
    try:
        with pytest.raises(RuntimeError, match="synthetic failure evidence error"):
            client.post("/scan/status/update", json=failed, headers=headers)
    finally:
        event.remove(ScanExecutionEvidence, "before_insert", fail_insert)
    with SessionLocal() as db:
        run = db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == start["run_id"]))
        assert run.status == "running"
        assert db.get(ScanExecutionEvidence, start["run_id"]) is None
    assert client.post("/scan/status/update", json=failed, headers=headers).status_code == 200


def test_failed_scan_can_record_a_proven_unreached_check(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    headers = auth_header_factory(tenant)
    start = _request(tenant)
    start["expectation"]["checks"][1]["enabled"] = True
    accepted = client.post("/scan/start", json=start, headers=headers)
    assert accepted.status_code == 200
    base = {"tenant_id": tenant["tenant_id"], "run_id": start["run_id"], "scan_mode": "data_health_score",
            "status": "running", "execution_token": accepted.json()["execution_token"],
            "worker_id": start["client_request_id"]}
    assert client.post("/scan/status/update", json=base, headers=headers).status_code == 200
    now = datetime.now(timezone.utc).isoformat()
    failed = dict(base, status="failed", failure_evidence={"schema_version": "bc-check-failure-partial-v1", "checks": [
        {"code": CHECK_A, "status": "FAILED", "finding_count": 0, "observed_at_utc": now},
        {"code": CHECK_B, "status": "NOT_EXECUTED", "finding_count": 0, "observed_at_utc": now}]})
    response = client.post("/scan/status/update", json=failed, headers=headers)
    assert response.status_code == 200, response.text
    with SessionLocal() as db:
        stored = db.get(ScanExecutionEvidence, start["run_id"])
        assert stored is not None and '"status":"NOT_EXECUTED"' in stored.payload_json


@pytest.mark.skipif(engine.dialect.name != "postgresql", reason="requires PostgreSQL concurrency")
def test_parallel_identical_failed_evidence_is_stored_once(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _bind(tenant)
    headers = auth_header_factory(tenant)
    start = _request(tenant)
    accepted = client.post("/scan/start", json=start, headers=headers)
    assert accepted.status_code == 200
    base = {"tenant_id": tenant["tenant_id"], "run_id": start["run_id"], "scan_mode": "data_health_score",
            "status": "running", "execution_token": accepted.json()["execution_token"],
            "worker_id": start["client_request_id"]}
    assert client.post("/scan/status/update", json=base, headers=headers).status_code == 200
    now = datetime.now(timezone.utc).isoformat()
    failed = dict(base, status="failed", failure_evidence={"schema_version": "bc-check-failure-partial-v1", "checks": [
        {"code": CHECK_A, "status": "FAILED", "finding_count": 0, "observed_at_utc": now}]})
    barrier = Barrier(2)
    def submit():
        barrier.wait()
        return client.post("/scan/status/update", json=failed, headers=headers)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: submit(), range(2)))
    assert [result.status_code for result in results] == [200, 200]
    with SessionLocal() as db:
        assert len(db.scalars(select(ScanExecutionEvidence).where(ScanExecutionEvidence.scan_id == start["run_id"])).all()) == 1


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
    second["expectation"]["checks"][1]["enabled"] = True
    barrier = Barrier(2)
    def submit(payload):
        barrier.wait()
        return client.post("/scan/start", json=payload, headers=headers)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(submit, (first, second)))
    assert sorted(result.status_code for result in results) == [200, 409]
    with SessionLocal() as db:
        assert len(db.scalars(select(ScanExpectationSnapshot).where(ScanExpectationSnapshot.scan_id == first["run_id"])).all()) == 1
