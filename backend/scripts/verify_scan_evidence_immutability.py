"""Verify migration guards using disposable synthetic rows in a local test DB."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.models import Scan, ScanExecutionEvidence, Tenant  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    args = parser.parse_args()
    url = make_url(args.database_url)
    if (url.get_backend_name() != "postgresql" or url.host not in {"localhost", "127.0.0.1", "::1"}
            or not (url.database or "").endswith("_test")):
        raise SystemExit("Refusing: requires a local PostgreSQL database ending in _test")
    engine = create_engine(url)
    now = datetime.now(timezone.utc)
    tenant_id, scan_id = f"evidence-{uuid4().hex}", f"evidence-{uuid4().hex}"
    company = "11111111-2222-3333-4444-555555555555"
    with Session(engine) as db:
        tenant = Tenant(tenant_id=tenant_id, environment_name="synthetic-test", app_version="test", created_at_utc=now)
        foreign_tenant_id = f"foreign-{uuid4().hex}"
        foreign_tenant = Tenant(tenant_id=foreign_tenant_id, environment_name="synthetic-test", app_version="test", created_at_utc=now)
        scan = Scan(scan_id=scan_id, tenant_id=tenant_id, scan_type="deep", generated_at_utc=now,
                    data_score=50, checks_count=1, issues_count=0, summary_headline="synthetic",
                    summary_rating="test", bc_company_id=company, lcy_code="EUR")
        db.add_all([tenant, foreign_tenant, scan])
        db.flush()
        for bad_tenant, bad_company in ((tenant_id, "wrong"), (foreign_tenant_id, company)):
            bad = ScanExecutionEvidence(scan_id=scan_id, tenant_id=bad_tenant, company_id=bad_company,
                                        schema_version="partial", payload_json="{}", payload_sha256="a" * 64,
                                        sync_sha256="b" * 64, created_at_utc=now)
            try:
                with db.begin_nested():
                    db.add(bad)
                    db.flush()
            except DBAPIError:
                pass
            else:
                raise AssertionError("Tenant/company binding trigger did not reject invalid evidence")
        db.add(ScanExecutionEvidence(scan_id=scan_id, tenant_id=tenant_id, company_id=company,
                                     schema_version="partial", payload_json="{}", payload_sha256="a" * 64,
                                     sync_sha256="b" * 64, created_at_utc=now))
        db.flush()
        for statement in ("UPDATE scan_execution_evidence SET payload_json='changed' WHERE scan_id=:id",
                          "DELETE FROM scan_execution_evidence WHERE scan_id=:id"):
            try:
                with db.begin_nested():
                    db.execute(text(statement), {"id": scan_id})
            except DBAPIError:
                pass
            else:
                raise AssertionError("Immutable evidence trigger did not reject mutation")
        # Verify the legitimate parent-retention cascade; the transaction is
        # rolled back at session exit, leaving no synthetic rows behind.
        db.execute(text("DELETE FROM scans WHERE scan_id=:id"), {"id": scan_id})
        assert db.execute(text("SELECT 1 FROM scan_execution_evidence WHERE scan_id=:id"), {"id": scan_id}).first() is None
        db.rollback()
    print("PASS: tenant/company binding, update/delete guards and parent-retention cascade")


if __name__ == "__main__":
    main()
