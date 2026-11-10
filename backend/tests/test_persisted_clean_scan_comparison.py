"""Narrow real-ORM integration for clean, fully evidenced scan pairs.

This does not authorize finding resolution, score/impact deltas or report export.
"""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select

from app.db import SessionLocal
from app.models import (
    Scan, ScanExecutionEvidence, ScanExpectationSnapshot, ScanRunStatus, Tenant,
)
from app.services.scan_catalog_contract import CHECK_MODULE_TO_RUN_MODULE, catalog_1_0_2_57
from app.services.scan_comparability_service import (
    Reason, catalog_fingerprint, compare_persisted_scans,
)

COMPANY = "11111111-2222-3333-4444-555555555555"
BASE = datetime(2026, 11, 10, 9, 0, tzinfo=timezone.utc)


def _saved_clean_scan(db, tenant_id, scan_id, started, *, exception_scope=None, evidence_hash_valid=True):
    catalog_version, _, catalog = catalog_1_0_2_57()
    pairs = sorted(catalog)
    selected = next(code for code, module in pairs if CHECK_MODULE_TO_RUN_MODULE[module] == "FINANCE")
    declared = [{"code": code, "module": module, "enabled": code == selected} for code, module in pairs]
    frozen = {
        "schema_version": "bc-scan-expectation-v2",
        "scan_id": scan_id, "tenant_id": tenant_id, "company_id": COMPANY,
        "environment": "sandbox", "currency": "EUR", "modules": ["FINANCE"],
        "catalog_version": catalog_version,
        "methodology_version": "bc-deep-scan-1.0.2.58",
        "checks": declared, "exception_scope": exception_scope if exception_scope is not None else [],
    }
    frozen["catalog_fingerprint"] = catalog_fingerprint(
        catalog_version, frozen["methodology_version"], tuple(pairs)
    )
    expectation_json = json.dumps(frozen, sort_keys=True, separators=(",", ":"))
    observed = {"schema_version": "bc-check-execution-partial-v1", "checks": [
        {"code": selected, "status": "PASS", "finding_count": 0,
         "observed_at_utc": (started + timedelta(minutes=2)).isoformat()},
    ]}
    observed_json = json.dumps(observed, sort_keys=True, separators=(",", ":"))
    db.add(Scan(
        scan_id=scan_id, tenant_id=tenant_id, scan_type="deep",
        generated_at_utc=started, data_score=100, checks_count=1, issues_count=0,
        summary_headline="Test scan", summary_rating="GOOD",
        bc_company_id=COMPANY, lcy_code="EUR",
    ))
    db.flush()
    db.add(ScanRunStatus(
        run_id=scan_id, tenant_id=tenant_id, status="completed",
        created_at_utc=started, updated_at_utc=started + timedelta(minutes=3),
        started_at_utc=started + timedelta(minutes=1),
        result_persisted_at_utc=started + timedelta(minutes=2, seconds=30),
        completed_at_utc=started + timedelta(minutes=3),
    ))
    db.add(ScanExpectationSnapshot(
        scan_id=scan_id, tenant_id=tenant_id, company_id=COMPANY,
        payload_json=expectation_json,
        payload_sha256=hashlib.sha256(expectation_json.encode()).hexdigest(),
        created_at_utc=started,
    ))
    db.add(ScanExecutionEvidence(
        scan_id=scan_id, tenant_id=tenant_id, company_id=COMPANY,
        schema_version="bc-check-execution-partial-v1",
        payload_json=observed_json,
        payload_sha256=hashlib.sha256(observed_json.encode()).hexdigest()
            if evidence_hash_valid else "f" * 64,
        sync_sha256="a" * 64, created_at_utc=started + timedelta(minutes=2),
    ))
    return selected


def test_two_persisted_clean_scans_have_verified_check_comparison(tenant_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    a, b = str(uuid4()), str(uuid4())
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        row.bc_company_id = COMPANY
        row.environment_name = "sandbox"
        db.flush()
        selected = _saved_clean_scan(db, tenant["tenant_id"], a, BASE)
        _saved_clean_scan(db, tenant["tenant_id"], b, BASE + timedelta(days=1))
        db.commit()
        result = compare_persisted_scans(db, tenant["tenant_id"], a, b)
        assert result.comparable and result.comparable_checks == (selected,)
        assert not result.health_score_comparable and not result.impact_comparable
        assert compare_persisted_scans(db, tenant["tenant_id"], b, a).reasons == (Reason.INVALID_SCAN_ORDER,)
        assert compare_persisted_scans(db, tenant["tenant_id"], a, a).reasons == (\n            Reason.INVALID_SCAN_ORDER, Reason.SAME_SCAN,\n        )
        assert compare_persisted_scans(db, "other-tenant", a, b).reasons == (Reason.MISSING_PROVENANCE,)


def test_tampered_payload_or_changed_exception_scope_fail_closed(tenant_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    a, b, c, d = (str(uuid4()) for _ in range(4))
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        row.bc_company_id = COMPANY
        row.environment_name = "sandbox"
        db.flush()
        _saved_clean_scan(db, tenant["tenant_id"], a, BASE)
        _saved_clean_scan(db, tenant["tenant_id"], b, BASE + timedelta(days=1), evidence_hash_valid=False)
        _saved_clean_scan(db, tenant["tenant_id"], c, BASE + timedelta(days=2),
                          exception_scope=[{"entry_no": 1, "table_id": 18,
                                            "record_system_id": str(uuid4()),
                                            "issue_code": "CUSTOMERS_MISSING_NAME"}])
        _saved_clean_scan(db, tenant["tenant_id"], d, BASE + timedelta(days=3))
        wrong_count = db.scalar(select(Scan).where(Scan.scan_id == d))
        wrong_count.checks_count = 199  # Snapshot deliberately enabled exactly one check.
        db.commit()
        assert compare_persisted_scans(db, tenant["tenant_id"], a, b).reasons == (Reason.MISSING_PROVENANCE,)
        assert compare_persisted_scans(db, tenant["tenant_id"], a, c).reasons == (Reason.SCOPE_MISMATCH,)
        assert compare_persisted_scans(db, tenant["tenant_id"], a, d).reasons == (Reason.MISSING_PROVENANCE,)
