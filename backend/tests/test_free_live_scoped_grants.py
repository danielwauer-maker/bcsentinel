"""BC-native Free report grants never unlock paid reports or cross-company data."""
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException
from sqlalchemy import select

from app.core.settings import settings
from app.db import SessionLocal
from app.models import Scan, ScanRunStatus, ScanStartRequest, Tenant
from app.services.report_archive_service import issue_free_link, redeem_code, verify_scoped_session

COMPANY = "6f1c2a3b-4d5e-6f70-8192-a3b4c5d6e7f8"


def _original_free(tenant_id: str, scan_id: str = "RUN_FREE_VALID"):
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
        tenant.bc_company_id = COMPANY
        scan = Scan(
            tenant_id=tenant_id, scan_id=scan_id, scan_type="data_health_score",
            bc_company_id=COMPANY, lcy_code="EUR", generated_at_utc=now,
            data_score=72, checks_count=199, issues_count=0, total_records=30,
        )
        db.add(scan)
        db.add(ScanStartRequest(
            tenant_id=tenant_id, client_request_id="eddf1f6e-2177-4bb1-a0d4-f90ad59cc10c",
            payload_hash="a" * 64, scan_id=scan_id,
            requested_scan_mode="data_health_score",
            resolved_product_code="data_health_score",
            free_scan_slot="data_health_score",
            status="accepted", created_at_utc=now, updated_at_utc=now,
        ))
        db.add(ScanRunStatus(
            tenant_id=tenant_id, run_id=scan_id, scan_mode="data_health_score",
            status="completed", created_at_utc=now, updated_at_utc=now,
            completed_at_utc=now, result_persisted_at_utc=now,
            progress_percent=100,
        ))
        db.commit()


def test_free_one_time_grant_is_company_bound_and_has_no_paid_entitlement(tenant_factory, monkeypatch):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    tenant_info = tenant_factory()
    _original_free(tenant_info["tenant_id"])
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_info["tenant_id"]))
        scan = db.scalar(select(Scan).where(Scan.scan_id == "RUN_FREE_VALID"))
        url = issue_free_link(db, tenant, scan, "https://reports.example")
    query = parse_qs(urlparse(url).query)
    assert query["variant"] == ["free"]
    assert query["companyId"] == [COMPANY]
    assert "api_token" not in url.lower()
    with SessionLocal() as db:
        token = redeem_code(db, query["code"][0])
    assert token["report_variant"] == "free"
    assert token["scan_id"] == "RUN_FREE_VALID"
    assert verify_scoped_session(
        "Bearer " + token["access_token"],
        scan_id="RUN_FREE_VALID", company_id=COMPANY, variant="free",
    ) == tenant_info["tenant_id"]
    assert verify_scoped_session(
        "Bearer " + token["access_token"],
        scan_id="RUN_FREE_VALID", company_id=COMPANY, variant="full",
    ) is None
    assert verify_scoped_session(
        "Bearer " + token["access_token"],
        scan_id="RUN_FREE_VALID", company_id="11111111-1111-1111-1111-111111111111", variant="free",
    ) is None
    with SessionLocal() as db:
        try:
            redeem_code(db, query["code"][0])
        except HTTPException as exc:
            assert exc.status_code == 403
        else:
            raise AssertionError("one-time code replay was accepted")


def test_incomplete_scan_does_not_issue_free_grant(tenant_factory, monkeypatch):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    info = tenant_factory()
    _original_free(info["tenant_id"])
    with SessionLocal() as db:
        run = db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == "RUN_FREE_VALID"))
        run.result_persisted_at_utc = None
        db.commit()
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == info["tenant_id"]))
        scan = db.scalar(select(Scan).where(Scan.scan_id == "RUN_FREE_VALID"))
        try:
            issue_free_link(db, tenant, scan, "https://reports.example")
        except HTTPException as exc:
            assert exc.status_code == 404
        else:
            raise AssertionError("incomplete Free scan received a grant")
