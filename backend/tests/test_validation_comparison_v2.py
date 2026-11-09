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
          lcy: str = "EUR", *, completed: bool = True, mode: str = "deep") -> Scan:
    scan = Scan(
        tenant_id=tenant_id, scan_id=scan_id, scan_type="deep",
        generated_at_utc=time, data_score=60, checks_count=10, issues_count=0,
        premium_available=True, summary_headline="test", summary_rating="ok",
        total_records=100, bc_company_id=company, lcy_code=lcy,
    )
    db.add(scan)
    db.flush()
    if completed:
        db.add(ScanRunStatus(
            run_id=scan_id, tenant_id=tenant_id, scan_mode=mode,
            status="completed", created_at_utc=time, updated_at_utc=time,
            completed_at_utc=time, result_persisted_at_utc=time,
        ))
        db.flush()
    return scan


def _scope(db, scan: Scan, *, version: int = 1, confirmed: bool = False,
           module: str = "system", original_free: bool = False) -> AssessmentScopeSnapshot:
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
    if original_free:
        db.add(TenantScanCredit(
            tenant_id=scan.tenant_id, product_code="free_entry", status="consumed",
            consumed_scan_id=scan.scan_id, created_at_utc=now, consumed_at_utc=now,
        ))
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
        _scope(db, initial, version=2, confirmed=True, original_free=True)
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
        _scope(db, initial, confirmed=True, original_free=True)
        malformed = _scan(db, tenant_id, "scope-malformed-company", start + timedelta(hours=1), "invalid")
        _scope(db, malformed)
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


def test_validation_scan_issues_only_its_own_report_link(
    client, monkeypatch, tenant_factory, auth_header_factory,
):
    from urllib.parse import parse_qs, urlsplit
    from app.core.settings import settings

    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    monkeypatch.setattr(settings, "REPORT_V6_VIEWER_BASE_URL", "https://reports.example.test")
    identity = tenant_factory(plan="free", license_status="active")
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter_by(tenant_id=identity["tenant_id"]).one()
        tenant.bc_company_id = COMPANY_A
        tenant.premium_until_utc = now + timedelta(days=1)
        initial = _scan(db, tenant.tenant_id, "validation-route-baseline", now - timedelta(days=1))
        _scope(db, initial, confirmed=True, original_free=True)
        current = _scan(db, tenant.tenant_id, "validation-route-current", now)
        _scope(db, current)
        _validation_credit(db, tenant.tenant_id, current.scan_id)
        db.commit()

    headers = auth_header_factory(identity)
    scan_id = "validation-route-current"
    full = client.post(f"/reports/executive/{scan_id}/v6-link", headers=headers)
    assert full.status_code == 409 and full.json()["detail"] == "WRONG_REPORT_VARIANT"
    issued = client.post(f"/reports/live/validation/{scan_id}/link", headers=headers)
    assert issued.status_code == 200, issued.text
    link = parse_qs(urlsplit(issued.json()["url"]).query)
    assert link["variant"] == ["validation"]
    body = {"code": link["code"][0], "scan_id": scan_id, "company_id": COMPANY_A, "report_variant": "validation"}
    exchanged = client.post("/reports/access/exchange", json=body)
    assert exchanged.status_code == 200, exchanged.text
    report = client.get(
        f"/account/reports/validation/{scan_id}",
        params={"company_id": COMPANY_A},
        headers={"Authorization": "Bearer " + exchanged.json()["access_token"]},
    )
    assert report.status_code == 200 and report.json()["variant"] == "validation"


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
        scan = _scan(db, tenant_id, "monitoring-comparison-source", now, mode="monitoring")
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
        scan = _scan(db, tenant_id, "monitoring-not-complete", datetime.now(timezone.utc), completed=False)
        with pytest.raises(HTTPException) as exc:
            _load_validation_scan(db, tenant, scan.scan_id)
        assert exc.value.status_code == 409
        db.rollback()


def test_unfinished_historical_scan_is_never_chosen_as_previous(tenant_factory):
    tenant_id = tenant_factory()["tenant_id"]
    start = datetime(2026, 11, 1, tzinfo=timezone.utc)
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        initial = _scan(db, tenant_id, "compare-finished-baseline", start)
        _scope(db, initial, confirmed=True, original_free=True)
        incomplete = _scan(
            db, tenant_id, "compare-incomplete-history",
            start + timedelta(days=1), completed=False,
        )
        _scope(db, incomplete)
        current = _scan(db, tenant_id, "compare-current-finished", start + timedelta(days=2))
        _scope(db, current)
        result = choose_validation_references(db, tenant, current)
        assert result.previous.scan_id == initial.scan_id
        db.rollback()
