"""Real SQLite Alembic migration and append-only source-record storage guards."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import sys

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError

from app.models import ScanRecordIdentityEvidence


BASE = Path(__file__).resolve().parents[1]
COMPANY = "11111111-2222-3333-4444-555555555555"
WHEN = "2026-11-10 10:00:00"


def _migrate(url: str, direction: str, revision: str, *, success=True) -> str:
    result = subprocess.run(
        [sys.executable, "-m", "alembic", direction, revision],
        cwd=BASE,
        env=dict(os.environ, DATABASE_URL=url),
        capture_output=True, text=True, timeout=120,
    )
    assert (result.returncode == 0) is success, result.stdout + result.stderr
    return result.stdout + result.stderr


def test_record_identity_evidence_migration_binds_and_seals_rows(tmp_path):
    url = "sqlite:///" + str(tmp_path / "record-evidence.sqlite3")
    _migrate(url, "upgrade", "head")
    engine = create_engine(url)
    assert "scan_record_identity_evidence" in inspect(engine).get_table_names()
    assert ScanRecordIdentityEvidence.__tablename__ == "scan_record_identity_evidence"

    with engine.begin() as db:
        db.execute(text(
            "INSERT INTO tenants (tenant_id, environment_name, app_version, created_at_utc, current_plan, license_status, bc_company_id) "
            "VALUES ('tenant-r', 'sandbox', '1.0.2.58', :dt, 'free', 'active', :company)"
        ), {"dt": WHEN, "company": COMPANY})
        db.execute(text(
            "INSERT INTO scans (scan_id, tenant_id, scan_type, generated_at_utc, data_score, checks_count, issues_count, "
            "summary_headline, summary_rating, bc_company_id, lcy_code) "
            "VALUES ('scan-r', 'tenant-r', 'deep', :dt, 90, 1, 1, 'test', 'good', :company, 'EUR')"
        ), {"dt": WHEN, "company": COMPANY})
        db.execute(text(
            "INSERT INTO scan_run_statuses (run_id, tenant_id, status, created_at_utc, updated_at_utc, result_persisted_at_utc) "
            "VALUES ('scan-r', 'tenant-r', 'completed', :dt, :dt, :dt)"
        ), {"dt": WHEN})
        db.execute(text(
            "INSERT INTO scan_expectation_snapshots (scan_id, tenant_id, company_id, payload_json, payload_sha256, created_at_utc) "
            "VALUES ('scan-r', 'tenant-r', :company, '{}', :sha, :dt)"
        ), {"company": COMPANY, "sha": hashlib.sha256(b'{}').hexdigest(), "dt": WHEN})
        db.execute(text(
            "INSERT INTO scan_execution_evidence (scan_id, tenant_id, company_id, schema_version, payload_json, payload_sha256, sync_sha256, created_at_utc) "
            "VALUES ('scan-r', 'tenant-r', :company, 'bc-check-execution-partial-v1', '{}', :sha, :sha, :dt)"
        ), {"company": COMPANY, "sha": hashlib.sha256(b'{}').hexdigest(), "dt": WHEN})

    insert = text(
        "INSERT INTO scan_record_identity_evidence "
        "(scan_id, tenant_id, company_id, check_code, schema_version, payload_json, payload_sha256, created_at_utc) "
        "VALUES (:scan, :tenant, :company, :check, 'bc-record-evidence-v1', :payload, :sha, :dt)"
    )
    args = {
        "scan": "scan-r", "tenant": "tenant-r", "company": COMPANY,
        "check": "CUSTOMERS_DUPLICATE_VAT", "payload": '{}',
        "sha": hashlib.sha256(b'{}').hexdigest(), "dt": WHEN,
    }
    with engine.begin() as db:
        with pytest.raises(IntegrityError, match="binding mismatch"):
            with db.begin_nested():
                db.execute(insert, args | {"tenant": "foreign-tenant"})
        with pytest.raises(IntegrityError, match="binding mismatch"):
            with db.begin_nested():
                db.execute(insert, args | {"company": "22222222-2222-4222-8222-222222222222"})
        with pytest.raises(IntegrityError):
            with db.begin_nested():
                db.execute(insert, args | {"check": "UNSUPPORTED_CHECK"})
        db.execute(insert, args)

    with engine.begin() as db:
        assert db.execute(text("SELECT COUNT(*) FROM scan_record_identity_evidence")).scalar_one() == 1
        with pytest.raises(IntegrityError, match="immutable"):
            with db.begin_nested():
                db.execute(text("UPDATE scan_record_identity_evidence SET payload_json='changed'"))
        with pytest.raises(IntegrityError, match="immutable"):
            with db.begin_nested():
                db.execute(text("DELETE FROM scan_record_identity_evidence"))

    # Rollback of a populated evidence table is prohibited.
    output = _migrate(url, "downgrade", "0039_scan_expectation_snapshot", success=False)
    assert "Refusing to drop nonempty scan record identity evidence" in output
    with engine.connect() as db:
        assert db.execute(text("SELECT COUNT(*) FROM scan_record_identity_evidence")).scalar_one() == 1
