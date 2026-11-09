"""V2 scan comparison: verified original baseline plus last comparable scan."""
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.assessment_scope_models import AssessmentScopeModule, AssessmentScopeSnapshot
from app.db import SessionLocal
from app.models import Scan, ScanRunStatus, Tenant, TenantScanCredit
from app.services.validation_comparison_v2_service import choose_validation_references

COMPANY_A = "11111111-2222-3333-4444-555555555555"
COMPANY_B = "99999999-2222-3333-4444-555555555555"


def _scan(db, tenant_id: str, scan_id: str, time: datetime, company: str = COMPANY_A,
          lcy: str = "EUR") -> Scan:
    scan = Scan(
        tenant_id=tenant_id, scan_id=scan_id, scan_type="deep",
        generated_at_utc=time, data_score=60, checks_count=10, issues_count=0,
        premium_available=True, summary_headline="test", summary_rating="ok",
        total_records=100, bc_company_id=company, lcy_code=lcy,
    )
    db.add(scan)
    db.flush()
    return scan


def _scope(db, scan: Scan, *, version: int = 1, confirmed: bool = False,
           module: str = "system") -> AssessmentScopeSnapshot:
    now = datetime.now(timezone.utc)
    scope = AssessmentScopeSnapshot(
        scan_id=scan.scan_id, tenant_id=scan.tenant_id, version=version,
        state="confirmed" if confirmed else "auto",
        source="customer_confirmation" if confirmed else "usage_detection",
        score_type="confirmed_baseline" if confirmed else "preliminary",
        score_value=scan.data_score, supported_modules_count=10,
        included_modules_count=1, unknown_modules_count=0,
        unsupported_extensions_json="[]", created_at_utc=now,
        confirmed_at_utc=now if confirmed else None,
    )
    db.add(scope)
    db.flush()
    db.add(AssessmentScopeModule(
        snapshot_id=scope.id, module_code=module, display_name=module,
        support_status="supported", detection_status="active",
        decision="include", included_in_score=1, confidence=1,
        detection_reason="test", module_score=60,
    ))
    db.flush()
    return scope


def _validation_credit(db, tenant_id: str, scan_id: str) -> None:
    db.add(TenantScanCredit(
        tenant_id=tenant_id, product_code="validation_check",
        status="consumed", source="test", consumed_scan_id=scan_id,
        created_at_utc=datetime.now(timezone.utc),
        consumed_at_utc=datetime.now(timezone.utc),
    ))
    db.flush()


def test_previous_validation_is_default_but_initial_confirmed_baseline_preserved(tenant_factory):
    tenant_id = tenant_factory()["tenant_id"]
    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        initial = _scan(db, tenant_id, "scope-v2-initial", start)
        _scope(db, initial)
        _scope(db, initial, version=2, confirmed=True)
        prior = _scan(db, tenant_id, "scope-v2-previous-validation", start + timedelta(days=7))
        _scope(db, prior)
        _validation_credit(db, tenant_id, prior.scan_id)
        current = _scan(db, tenant_id, "scope-v2-current-validation", start + timedelta(days=14))
        _scope(db, current)
        _validation_credit(db, tenant_id, current.scan_id)
        ref = choose_validation_references(db, tenant, current)
        assert ref.initial.scan_id == initial.scan_id
        assert ref.previous.scan_id == prior.scan_id
        assert ref.scope_version == 2
        db.rollback()


def test_cross_company_and_cross_currency_scans_never_become_comparators(tenant_factory):
    tenant_id = tenant_factory()["tenant_id"]
    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        initial = _scan(db, tenant_id, "scope-cross-initial", start)
        _scope(db, initial, confirmed=True)
        wrong_company = _scan(db, tenant_id, "scope-cross-company", start + timedelta(days=1), COMPANY_B)
        _scope(db, wrong_company)
        wrong_currency = _scan(db, tenant_id, "scope-cross-currency", start + timedelta(days=2), lcy="USD")
        _scope(db, wrong_currency)
        current = _scan(db, tenant_id, "scope-cross-current", start + timedelta(days=3))
        _scope(db, current)
        ref = choose_validation_references(db, tenant, current)
        assert ref.previous.scan_id == initial.scan_id
        assert ref.initial.scan_id == initial.scan_id
        db.rollback()


def test_unconfirmed_baseline_is_rejected_not_autoconfirmed(tenant_factory):
    tenant_id = tenant_factory()["tenant_id"]
    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        initial = _scan(db, tenant_id, "scope-v2-unconfirmed", start)
        _scope(db, initial)
        current = _scan(db, tenant_id, "scope-v2-new", start + timedelta(days=1))
        _scope(db, current)
        with pytest.raises(HTTPException) as exc:
            choose_validation_references(db, tenant, current)
        assert exc.value.status_code == 409
        assert "original confirmed" in exc.value.detail
        db.rollback()


def test_missing_current_scope_is_rejected(tenant_factory):
    tenant_id = tenant_factory()["tenant_id"]
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        current = _scan(db, tenant_id, "scope-no-current", datetime.now(timezone.utc))
        with pytest.raises(HTTPException) as exc:
            choose_validation_references(db, tenant, current)
        assert exc.value.status_code == 409
        assert "current scan scope" in exc.value.detail
        db.rollback()


def test_foreign_tenant_cannot_read_scan(tenant_factory):
    a = tenant_factory()["tenant_id"]
    b = tenant_factory()["tenant_id"]
    with SessionLocal() as db:
        owner = db.query(Tenant).filter_by(tenant_id=a).one()
        current = _scan(db, b, "scope-other-tenant", datetime.now(timezone.utc))
        with pytest.raises(HTTPException) as exc:
            choose_validation_references(db, owner, current)
        assert exc.value.status_code == 404
        db.rollback()



def test_monitoring_scan_is_valid_validation_source_without_scan_credit(tenant_factory):
    from app.core.settings import settings
    from app.services.validation_report_service import _load_validation_scan
    tenant_id = tenant_factory()["tenant_id"]
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        scan = _scan(db, tenant_id, "monitoring-comparison-source", now)
        db.add(ScanRunStatus(
            run_id=scan.scan_id, tenant_id=tenant_id, scan_mode="monitoring",
            status="completed", created_at_utc=now, updated_at_utc=now,
            completed_at_utc=now, result_persisted_at_utc=now,
        ))
        db.flush()
        previous_flag = settings.ACCESS_MODEL_V2_ENABLED
        settings.ACCESS_MODEL_V2_ENABLED = True
        try:
            result, credit = _load_validation_scan(db, tenant, scan.scan_id)
            assert result.scan_id == scan.scan_id
            assert credit is None
        finally:
            settings.ACCESS_MODEL_V2_ENABLED = previous_flag
        db.rollback()


def test_unfinished_monitoring_scan_cannot_be_a_validation_source(tenant_factory, monkeypatch):
    from app.core.settings import settings
    from app.services.validation_report_service import _load_validation_scan
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    tenant_id = tenant_factory()["tenant_id"]
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        scan = _scan(db, tenant_id, "monitoring-not-complete", datetime.now(timezone.utc))
        with pytest.raises(HTTPException) as exc:
            _load_validation_scan(db, tenant, scan.scan_id)
        assert exc.value.status_code == 409
        db.rollback()
