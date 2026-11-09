from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.db import SessionLocal, engine
from app.models import Scan, ScanExecutionEvidence, ScanRunStatus, Tenant
from app.services.scan_comparability_service import Reason, compare_persisted_scans
from app.core.settings import settings
from test_product_licensing_p0 import _deep_scan_payload


COMPANY = "11111111-2222-3333-4444-555555555555"


def _start(client, tenant, headers):
    scan_id, worker = str(uuid4()), str(uuid4())
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        row.bc_company_id = COMPANY
        db.commit()
    response = client.post("/scan/start", headers=headers, json={
        "tenant_id": tenant["tenant_id"], "run_id": scan_id,
        "client_request_id": worker, "scan_mode": "data_health_score", "total_modules": 1,
    })
    assert response.status_code == 200, response.text
    payload = _deep_scan_payload(tenant["tenant_id"], scan_id)
    payload.update(scan_type="data_health_score", bc_company_id=COMPANY, lcy_code="EUR",
                   execution_token=response.json()["execution_token"], worker_id=worker)
    payload["check_execution_evidence"] = {
        "schema_version": "bc-check-execution-partial-v1",
        "checks": [
            {"code": "CHECK_A", "status": "PASS", "finding_count": 0, "observed_at_utc": datetime.now(timezone.utc).isoformat()},
            {"code": "CHECK_B", "status": "SKIPPED", "finding_count": 0, "observed_at_utc": datetime.now(timezone.utc).isoformat()},
        ],
    }
    return scan_id, payload


def test_leased_sync_stores_partial_evidence_and_rejects_changed_retry(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    headers = auth_header_factory(tenant)
    scan_id, payload = _start(client, tenant, headers)
    response = client.post("/scan/sync", headers=headers, json=payload)
    assert response.status_code == 200, response.text
    with SessionLocal() as db:
        evidence = db.get(ScanExecutionEvidence, scan_id)
        assert evidence is not None and evidence.schema_version == "bc-check-execution-partial-v1"
        assert evidence.tenant_id == tenant["tenant_id"] and evidence.company_id == COMPANY
        original_hash = evidence.payload_sha256
        original_persisted_at = db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == scan_id)).result_persisted_at_utc
        verdict = compare_persisted_scans(db, tenant["tenant_id"], scan_id, scan_id)
        assert verdict.reasons == (Reason.MISSING_PROVENANCE,)
        assert not verdict.comparable and not verdict.health_score_comparable and not verdict.impact_comparable
    replay = client.post("/scan/sync", headers=headers, json=payload)
    assert replay.status_code == 200, replay.text
    reordered = dict(payload)
    reordered["check_execution_evidence"] = dict(payload["check_execution_evidence"], checks=list(reversed(payload["check_execution_evidence"]["checks"])))
    assert client.post("/scan/sync", headers=headers, json=reordered).status_code == 200
    wrong_worker = dict(payload, worker_id=str(uuid4()))
    assert client.post("/scan/sync", headers=headers, json=wrong_worker).status_code == 409
    modified_scan = dict(payload, data_score=payload["data_score"] - 1)
    assert client.post("/scan/sync", headers=headers, json=modified_scan).status_code == 409
    omitted = dict(payload)
    omitted.pop("check_execution_evidence")
    assert client.post("/scan/sync", headers=headers, json=omitted).status_code == 409
    payload["check_execution_evidence"]["checks"][0]["status"] = "SKIPPED"
    altered = client.post("/scan/sync", headers=headers, json=payload)
    assert altered.status_code == 409
    with SessionLocal() as db:
        assert db.get(ScanExecutionEvidence, scan_id).payload_sha256 == original_hash
        assert db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == scan_id)).result_persisted_at_utc == original_persisted_at


def test_invalid_or_foreign_evidence_cannot_persist(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    headers = auth_header_factory(tenant)
    scan_id, payload = _start(client, tenant, headers)
    payload["execution_token"] = str(uuid4())
    response = client.post("/scan/sync", headers=headers, json=payload)
    assert response.status_code == 409
    with SessionLocal() as db:
        assert db.get(ScanExecutionEvidence, scan_id) is None


def test_duplicate_or_inconsistent_observations_are_rejected(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    headers = auth_header_factory(tenant)
    scan_id, payload = _start(client, tenant, headers)
    payload["check_execution_evidence"]["checks"].append(payload["check_execution_evidence"]["checks"][0])
    assert client.post("/scan/sync", headers=headers, json=payload).status_code == 422
    with SessionLocal() as db:
        assert db.get(ScanExecutionEvidence, scan_id) is None


def test_non_utc_observation_is_rejected(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    headers = auth_header_factory(tenant)
    _, payload = _start(client, tenant, headers)
    payload["check_execution_evidence"]["checks"][0]["observed_at_utc"] = "2026-11-09T12:00:00+01:00"
    assert client.post("/scan/sync", headers=headers, json=payload).status_code == 422


def test_pass_cannot_contradict_an_actual_finding(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    headers = auth_header_factory(tenant)
    scan_id, payload = _start(client, tenant, headers)
    payload["check_execution_evidence"]["checks"][0]["code"] = "SMOKE_ISSUE"
    assert client.post("/scan/sync", headers=headers, json=payload).status_code == 422
    with SessionLocal() as db:
        assert db.get(ScanExecutionEvidence, scan_id) is None
    payload["check_execution_evidence"]["checks"][0].update(status="FINDINGS", finding_count=1)
    response = client.post("/scan/sync", headers=headers, json=payload)
    assert response.status_code == 200, response.text


@pytest.mark.parametrize("status", ["FAILED", "NOT_EXECUTED"])
def test_partial_schema_does_not_invent_unsupported_execution_status(client, tenant_factory, auth_header_factory, status):
    tenant = tenant_factory(plan="free", license_status="active")
    headers = auth_header_factory(tenant)
    scan_id, payload = _start(client, tenant, headers)
    payload["check_execution_evidence"]["checks"][0]["status"] = status
    assert client.post("/scan/sync", headers=headers, json=payload).status_code == 422
    with SessionLocal() as db:
        assert db.get(ScanExecutionEvidence, scan_id) is None


def test_completed_historical_scan_is_not_backfilled(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    headers = auth_header_factory(tenant)
    scan_id, payload = _start(client, tenant, headers)
    legacy = dict(payload)
    legacy.pop("check_execution_evidence")
    assert client.post("/scan/sync", headers=headers, json=legacy).status_code == 200
    assert client.post("/scan/sync", headers=headers, json=payload).status_code == 409
    with SessionLocal() as db:
        assert db.get(ScanExecutionEvidence, scan_id) is None


def test_company_mismatch_is_rejected(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    headers = auth_header_factory(tenant)
    scan_id, payload = _start(client, tenant, headers)
    payload["bc_company_id"] = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    assert client.post("/scan/sync", headers=headers, json=payload).status_code == 409
    with SessionLocal() as db:
        assert db.get(ScanExecutionEvidence, scan_id) is None


def test_foreign_tenant_cannot_submit_execution_evidence(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    other = tenant_factory(plan="free", license_status="active")
    scan_id, payload = _start(client, tenant, auth_header_factory(tenant))
    response = client.post("/scan/sync", headers=auth_header_factory(other), json=payload)
    assert response.status_code == 403
    with SessionLocal() as db:
        assert db.get(ScanExecutionEvidence, scan_id) is None


@pytest.mark.skipif(engine.dialect.name != "postgresql", reason="Requires PostgreSQL row locking")
def test_parallel_identical_syncs_create_one_snapshot(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    headers = auth_header_factory(tenant)
    scan_id, payload = _start(client, tenant, headers)
    barrier = Barrier(2)

    def sync():
        barrier.wait(timeout=15)
        return client.post("/scan/sync", headers=headers, json=payload)

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: sync(), range(2)))
    assert [response.status_code for response in responses] == [200, 200], [r.text for r in responses]
    with SessionLocal() as db:
        assert len(db.scalars(select(ScanExecutionEvidence).where(ScanExecutionEvidence.scan_id == scan_id)).all()) == 1


@pytest.mark.skipif(engine.dialect.name != "postgresql", reason="Requires PostgreSQL row locking")
def test_parallel_different_syncs_do_not_overwrite_snapshot(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    headers = auth_header_factory(tenant)
    scan_id, payload = _start(client, tenant, headers)
    changed = dict(payload, data_score=payload["data_score"] - 1)
    barrier = Barrier(2)

    def sync(body):
        barrier.wait(timeout=15)
        return client.post("/scan/sync", headers=headers, json=body)

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(sync, (payload, changed)))
    assert sorted(response.status_code for response in responses) == [200, 409], [r.text for r in responses]
    with SessionLocal() as db:
        assert len(db.scalars(select(ScanExecutionEvidence).where(ScanExecutionEvidence.scan_id == scan_id)).all()) == 1


def test_monitoring_uses_shared_adapter_and_marks_historical_scan_unverified(monkeypatch, tenant_factory, scan_factory):
    import app.services.monitoring_report_service as service

    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    monkeypatch.setattr(service, "build_product_access_snapshot", lambda db, tenant: {"monitoring_active": True})
    tenant = tenant_factory(license_status="active")
    scan_id = "historical-monitoring-without-evidence"
    scan_factory(tenant_id=tenant["tenant_id"], scan_id=scan_id)
    with SessionLocal() as db:
        owner = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        owner.bc_company_id = COMPANY
        scan = db.scalar(select(Scan).where(Scan.scan_id == scan_id))
        scan.bc_company_id = COMPANY
        db.flush()
        report = service.build_monitoring_report(db, owner, scan_id)
        assert report.comparison_evidence.reason_codes == ["MISSING_PROVENANCE"]
        assert not report.comparison_evidence.comparable
        assert not report.comparison_evidence.health_score_comparable
