"""HTTP/ORM coverage for the guarded source-record identity sync path."""
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select

from app.db import SessionLocal
from app.models import ScanRecordIdentityEvidence, ScanRunStatus, Tenant
from app.services.scan_catalog_contract import catalog_1_0_2_57
from test_product_licensing_p0 import _deep_scan_payload

COMPANY = "11111111-2222-3333-4444-555555555555"
A = "aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa"
B = "bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb"
CHECK = "CUSTOMERS_DUPLICATE_VAT"


def _prepare(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        row.bc_company_id = COMPANY
        row.environment_name = "production"
        db.commit()

    headers = auth_header_factory(tenant)
    catalog_version, methodology, catalog = catalog_1_0_2_57()
    run_id, client_request = str(uuid4()), str(uuid4())
    start = {
        "tenant_id": tenant["tenant_id"], "run_id": run_id,
        "client_request_id": client_request, "scan_mode": "data_health_score",
        "total_modules": 1, "environment_name": "production",
        "expectation": {
            "schema_version": "bc-scan-expectation-v2",
            "methodology_version": "bc-deep-scan-1.0.2.58",
            "catalog_version": catalog_version,
            "company_id": COMPANY, "environment": "production",
            "currency": "EUR", "modules": ["FINANCE"],
            "exception_scope": [],
            "checks": [{"code": code, "module": module, "enabled": code == CHECK}
                       for code, module in sorted(catalog)],
        },
    }
    response = client.post("/scan/start", headers=headers, json=start)
    assert response.status_code == 200, response.text
    now = datetime.now(timezone.utc).isoformat()
    payload = _deep_scan_payload(tenant["tenant_id"], run_id)
    payload.update(
        scan_type="data_health_score", bc_company_id=COMPANY,
        lcy_code="EUR", checks_count=1, enabled_modules=["Finance"],
        execution_token=response.json()["execution_token"], worker_id=client_request,
    )
    payload["issues"][0].update(code=CHECK, affected_count=2)
    payload["check_execution_evidence"] = {
        "schema_version": "bc-check-execution-partial-v1",
        "checks": [{"code": CHECK, "status": "FINDINGS",
                    "finding_count": 1, "observed_at_utc": now}],
    }
    payload["source_record_evidence"] = {
        "schema_version": "bc-record-evidence-v1",
        "tenant_id": tenant["tenant_id"], "scan_id": run_id,
        "company_id": COMPANY, "check_code": CHECK,
        "observed_at_utc": now, "completed": True,
        "affected_records_count": 2,
        "records": [{"table_id": 18, "record_system_id": A},
                    {"table_id": 18, "record_system_id": B}],
    }
    return tenant, headers, payload


def test_sync_atomically_stores_and_replays_source_record_evidence(client, tenant_factory, auth_header_factory):
    tenant, headers, payload = _prepare(client, tenant_factory, auth_header_factory)
    run_id = payload["scan_id"]
    first = client.post("/scan/sync", json=payload, headers=headers)
    assert first.status_code == 200, first.text
    with SessionLocal() as db:
        row = db.get(ScanRecordIdentityEvidence, (run_id, CHECK))
        assert row is not None and row.company_id == COMPANY
        first_hash = row.payload_sha256
        assert db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == run_id)).status == "completed"

    retry = deepcopy(payload)
    retry["source_record_evidence"]["records"].reverse()
    replay = client.post("/scan/sync", json=retry, headers=headers)
    assert replay.status_code == 200, replay.text
    with SessionLocal() as db:
        assert db.get(ScanRecordIdentityEvidence, (run_id, CHECK)).payload_sha256 == first_hash

    missing = deepcopy(payload)
    del missing["source_record_evidence"]
    assert client.post("/scan/sync", json=missing, headers=headers).status_code == 409

    changed = deepcopy(payload)
    changed["source_record_evidence"]["records"][0]["record_system_id"] = str(uuid4())
    assert client.post("/scan/sync", json=changed, headers=headers).status_code == 409


def test_bad_company_or_membership_rejected_before_finalization(client, tenant_factory, auth_header_factory):
    tenant, headers, payload = _prepare(client, tenant_factory, auth_header_factory)
    run_id = payload["scan_id"]
    for change in (
        {"company_id": str(uuid4())},
        {"affected_records_count": 1},
        {"records": [{"table_id": 18, "record_system_id": A}]},
        {"observed_at_utc": "2020-01-01T00:00:00+00:00"},
    ):
        bad = deepcopy(payload)
        bad["source_record_evidence"].update(change)
        assert client.post("/scan/sync", json=bad, headers=headers).status_code in {409, 422}
        with SessionLocal() as db:
            assert db.get(ScanRecordIdentityEvidence, (run_id, CHECK)) is None
            assert db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == run_id)).status != "completed"

    response = client.post("/scan/sync", json=payload, headers=headers)
    assert response.status_code == 200, response.text


def test_wrong_lease_cannot_store_record_evidence(client, tenant_factory, auth_header_factory):
    tenant, headers, payload = _prepare(client, tenant_factory, auth_header_factory)
    wrong = deepcopy(payload)
    wrong["execution_token"] = str(uuid4())
    assert client.post("/scan/sync", json=wrong, headers=headers).status_code == 409
    with SessionLocal() as db:
        assert db.get(ScanRecordIdentityEvidence, (payload["scan_id"], CHECK)) is None


def test_optional_record_field_preserves_preexisting_sync_fingerprint():
    import hashlib
    import json
    from app.routers.scans import ScanSyncPayload, _canonical_execution_evidence

    old = _deep_scan_payload("legacy-tenant", "legacy-scan")
    old["check_execution_evidence"] = {
        "schema_version": "bc-check-execution-partial-v1",
        "checks": [{"code": "SMOKE_ISSUE", "status": "FINDINGS",
                    "finding_count": 1, "observed_at_utc": datetime.now(timezone.utc).isoformat()}],
    }
    parsed = ScanSyncPayload.model_validate(old)
    actual_hash = _canonical_execution_evidence(parsed)[2]
    legacy = parsed.model_dump(
        mode="json", exclude={"execution_token", "worker_id", "correlation_id", "source_record_evidence"}
    )
    legacy["check_execution_evidence"]["checks"].sort(key=lambda item: item["code"])
    legacy["enabled_modules"].sort()
    legacy["issues"].sort(key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    canonical = json.dumps(legacy, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    assert actual_hash == hashlib.sha256(canonical.encode()).hexdigest()
