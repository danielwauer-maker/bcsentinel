"""Real PostgreSQL Alembic + append-only record Evidence security checks.

Runs only with BCSENTINEL_TEST_DATABASE_URL set to an isolated PostgreSQL
CI instance. Creates a disposable sibling database, migrates it from scratch,
seeds a valid source graph, then tests trigger and constraint rejection.
Never targets a deployed DEV/PROD DB or the shared pytest fixture DB.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError

BASE = Path(__file__).resolve().parents[1]
PG_TEST_URL = os.environ.get("BCSENTINEL_TEST_DATABASE_URL", "")
COMPANY = "11111111-2222-4333-8444-555555555555"
OTHER_COMPANY = "22222222-2222-4333-8444-555555555555"
STAMP = "2026-11-10 10:00:00+00"
SHA = hashlib.sha256(b"{}").hexdigest()
TABLES = (
    "scan_execution_evidence",
    "scan_expectation_snapshots",
    "scan_record_identity_evidence",
)


@pytest.fixture(scope="module")
def migrated_postgresql():
    if not PG_TEST_URL or not PG_TEST_URL.startswith("postgresql"):
        pytest.skip("Dedicated PostgreSQL CI service not provided.")
    # Explicitly prohibit accidental external target databases.
    url = make_url(PG_TEST_URL)
    if url.host not in {"localhost", "127.0.0.1"} or url.database != "bcsentinel_report_test":
        pytest.skip("Migration security tests require the disposable local CI PostgreSQL database.")
    dbname = "bcs_pgte_" + uuid4().hex[:16]
    maintenance = create_engine(PG_TEST_URL, isolation_level="AUTOCOMMIT")
    test_url = url.set(database=dbname)
    test_engine = None
    try:
        with maintenance.connect() as conn:
            conn.execute(text(f'CREATE DATABASE "{dbname}"'))
        env = dict(os.environ, DATABASE_URL=test_url.render_as_string(hide_password=False))
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=BASE, env=env, text=True, capture_output=True, timeout=120,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        test_engine = create_engine(test_url)
        with test_engine.connect() as conn:
            assert conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == (
                "0040_scan_record_identity_evidence"
            )
        yield test_engine
    finally:
        if test_engine is not None:
            test_engine.dispose()
        with maintenance.connect() as conn:
            conn.execute(text(f'DROP DATABASE IF EXISTS "{dbname}" WITH (FORCE)'))
        maintenance.dispose()


@pytest.fixture
def seeded(migrated_postgresql):
    engine = migrated_postgresql
    with engine.begin() as conn:
        conn.execute(text(
            "INSERT INTO tenants (tenant_id, environment_name, app_version, created_at_utc, "
            "current_plan, license_status, bc_company_id) "
            "VALUES ('tenant-pg', 'sandbox', '1.0.2.58', :dt, 'free', 'active', :company)"
        ), {"dt": STAMP, "company": COMPANY})
        conn.execute(text(
            "INSERT INTO scans (scan_id, tenant_id, scan_type, generated_at_utc, data_score, "
            "checks_count, issues_count, summary_headline, summary_rating, bc_company_id, lcy_code) "
            "VALUES ('scan-pg', 'tenant-pg', 'deep', :dt, 90, 1, 1, 'test', 'good', :company, 'EUR')"
        ), {"dt": STAMP, "company": COMPANY})
        conn.execute(text(
            "INSERT INTO scan_run_statuses "
            "(run_id, tenant_id, status, created_at_utc, updated_at_utc, result_persisted_at_utc) "
            "VALUES ('scan-pg', 'tenant-pg', 'completed', :dt, :dt, :dt)"
        ), {"dt": STAMP})
    return engine


def _insert_statement(table: str):
    extra = {
        "scan_execution_evidence":
            "schema_version, payload_json, payload_sha256, sync_sha256",
        "scan_expectation_snapshots": "payload_json, payload_sha256",
        "scan_record_identity_evidence":
            "check_code, schema_version, payload_json, payload_sha256",
    }[table]
    extra_vals = {
        "scan_execution_evidence":
            "'bc-check-execution-partial-v1', '{}', :sha, :sha",
        "scan_expectation_snapshots": "'{}', :sha",
        "scan_record_identity_evidence":
            ":check, :schema, '{}', :sha",
    }[table]
    return text(
        f"INSERT INTO {table} "
        f"(scan_id, tenant_id, company_id, {extra}, created_at_utc) "
        f"VALUES (:scan, :tenant, :company, {extra_vals}, :dt)"
    )


def _args():
    return {
        "scan": "scan-pg", "tenant": "tenant-pg", "company": COMPANY,
        "check": "CUSTOMERS_DUPLICATE_VAT", "schema": "bc-record-evidence-v1",
        "sha": SHA, "dt": STAMP,
    }


def _reject(conn, statement, args, expected: str):
    # PostgreSQL marks a statement-error transaction as aborted, so isolate
    # every negative assertion within its own SAVEPOINT.
    with pytest.raises(DBAPIError, match=re.escape(expected)):
        with conn.begin_nested():
            conn.execute(statement, args)


@pytest.mark.parametrize("table,expected", [
    ("scan_execution_evidence", "scan execution evidence binding mismatch"),
    ("scan_expectation_snapshots", "scan expectation binding mismatch"),
    ("scan_record_identity_evidence", "scan record identity binding mismatch"),
])
def test_pg_binding_rejects_wrong_company_and_tenant(seeded, table, expected):
    engine = seeded
    with engine.begin() as conn:
        args = _args()
        _reject(conn, _insert_statement(table), args | {"company": OTHER_COMPANY}, expected)
        _reject(conn, _insert_statement(table), args | {"tenant": "foreign-tenant"}, expected)
        assert conn.execute(text(f"SELECT count(*) FROM {table}")).scalar_one() == 0


def test_pg_record_constraints_require_valid_parent_and_canonical_fields(seeded):
    engine = seeded
    args = _args()
    with engine.begin() as conn:
        # Insert the prerequisite rows with correct parent binding.
        conn.execute(_insert_statement("scan_expectation_snapshots"), args)
        conn.execute(_insert_statement("scan_execution_evidence"), args)
        # Parent binding passes; only table CHECK constraints can reject now.
        insert = _insert_statement("scan_record_identity_evidence")
        for modification, named_constraint in [
            ({"check": "INVALID_CHECK"}, "ck_record_evidence_check"),
            ({"schema": "invalid-version"}, "ck_record_evidence_schema"),
            ({"sha": "not-a-sha"}, "ck_record_evidence_sha256_length"),
        ]:
            _reject(conn, insert, args | modification, named_constraint)
        conn.execute(insert, args)
        assert conn.execute(text(
            "SELECT count(*) FROM scan_record_identity_evidence"
        )).scalar_one() == 1


def test_pg_immutability_for_each_evidence_table(seeded):
    args = _args()
    with seeded.begin() as conn:
        for table in ("scan_expectation_snapshots", "scan_execution_evidence",
                      "scan_record_identity_evidence"):
            conn.execute(_insert_statement(table), args)
        for table in TABLES:
            _reject(conn, text(f"UPDATE {table} SET payload_json='tampered'"),
                    {}, "is immutable")
            _reject(conn, text(f"DELETE FROM {table}"), {}, "is immutable")
            assert conn.execute(text(f"SELECT count(*) FROM {table}")).scalar_one() == 1


def test_pg_populated_evidence_blocks_downgrade(seeded):
    args = _args()
    with seeded.begin() as conn:
        for table in ("scan_expectation_snapshots", "scan_execution_evidence",
                      "scan_record_identity_evidence"):
            conn.execute(_insert_statement(table), args)
    # A deliberately failing downgrade on a disposable migrated database.
    url = seeded.url.render_as_string(hide_password=False)
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "downgrade", "0039_scan_expectation_snapshot"],
        cwd=BASE, env=dict(os.environ, DATABASE_URL=url),
        text=True, capture_output=True, timeout=120,
    )
    assert result.returncode != 0
    assert "Refusing to drop nonempty scan record identity evidence" in (
        result.stderr + result.stdout
    )
    with seeded.connect() as conn:
        assert conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == (
            "0040_scan_record_identity_evidence"
        )
