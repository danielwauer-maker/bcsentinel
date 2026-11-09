"""Database-level regression for Full 14d and Renewal checkout grant semantics."""
from datetime import datetime, timedelta, timezone

import pytest

from app.core.settings import settings
from app.db import SessionLocal
from app.models import Tenant, TenantProductEntitlement, TenantScanCredit, ScanRunStatus
from app.services.product_license_service import (
    PRODUCT_FULL_ASSESSMENT_V2,
    PRODUCT_ACCESS_RENEWAL,
    PRODUCT_ACCESS_RENEWAL_VALIDATION,
    grant_v2_access_purchase,
    record_product_purchase,
    build_product_access_snapshot,
    resolve_product_features,
    is_original_free_scan,
)


@pytest.fixture(autouse=True)
def enable_v2_model(monkeypatch):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)


def _purchase(db, tenant_id, code, session):
    return record_product_purchase(
        db, tenant_id=tenant_id, product_code=code,
        provider="test", provider_checkout_session_id=session,
        provider_payment_intent_id=None, status="paid",
        currency="EUR", amount_total=99.0,
    )


def test_full_unlock_does_not_issue_scan_credit_and_expiry_is_fourteen_days(tenant_factory):
    tenant_id = tenant_factory()["tenant_id"]
    with SessionLocal() as db:
        before = datetime.now(timezone.utc)
        purchase = _purchase(db, tenant_id, PRODUCT_FULL_ASSESSMENT_V2, "checkout-full")
        grant = grant_v2_access_purchase(
            db, tenant_id=tenant_id, product_code=PRODUCT_FULL_ASSESSMENT_V2,
            purchase_id=purchase.id,
        )
        db.commit()
        assert before + timedelta(days=13, hours=23) < grant.valid_until_utc.replace(tzinfo=timezone.utc) < before + timedelta(days=14, minutes=1)
        assert db.query(TenantScanCredit).filter_by(tenant_id=tenant_id).count() == 0
        assert build_product_access_snapshot(db, db.query(Tenant).filter_by(tenant_id=tenant_id).one())["premium_active"]


def test_renewal_stacks_active_days_and_payment_replay_is_idempotent(tenant_factory):
    tenant_id = tenant_factory()["tenant_id"]
    with SessionLocal() as db:
        first = _purchase(db, tenant_id, PRODUCT_FULL_ASSESSMENT_V2, "checkout-first")
        first_grant = grant_v2_access_purchase(
            db, tenant_id=tenant_id, product_code=PRODUCT_FULL_ASSESSMENT_V2,
            purchase_id=first.id,
        )
        original_end = first_grant.valid_until_utc
        renewal = _purchase(db, tenant_id, PRODUCT_ACCESS_RENEWAL, "checkout-second")
        renewal_grant = grant_v2_access_purchase(
            db, tenant_id=tenant_id, product_code=PRODUCT_ACCESS_RENEWAL,
            purchase_id=renewal.id,
        )
        assert renewal_grant.valid_until_utc - original_end == timedelta(days=14)
        count = db.query(TenantProductEntitlement).filter_by(tenant_id=tenant_id).count()
        replay = grant_v2_access_purchase(
            db, tenant_id=tenant_id, product_code=PRODUCT_ACCESS_RENEWAL,
            purchase_id=renewal.id,
        )
        assert replay.id == renewal_grant.id
        assert db.query(TenantProductEntitlement).filter_by(tenant_id=tenant_id).count() == count
        assert db.query(TenantScanCredit).filter_by(tenant_id=tenant_id).count() == 0
        db.commit()


def test_validation_renewal_issues_exactly_one_credit_even_on_replay(tenant_factory):
    tenant_id = tenant_factory()["tenant_id"]
    with SessionLocal() as db:
        purchase = _purchase(db, tenant_id, PRODUCT_ACCESS_RENEWAL_VALIDATION, "checkout-validation")
        a = grant_v2_access_purchase(
            db, tenant_id=tenant_id, product_code=PRODUCT_ACCESS_RENEWAL_VALIDATION,
            purchase_id=purchase.id,
        )
        b = grant_v2_access_purchase(
            db, tenant_id=tenant_id, product_code=PRODUCT_ACCESS_RENEWAL_VALIDATION,
            purchase_id=purchase.id,
        )
        assert a.id == b.id
        credits = db.query(TenantScanCredit).filter_by(tenant_id=tenant_id).all()
        assert len(credits) == 1
        assert credits[0].product_code == "validation_check"
        assert credits[0].status == "available"
        assert credits[0].source_purchase_id == purchase.id
        db.commit()


def test_unpaid_purchase_cannot_grant_access(tenant_factory):
    tenant_id = tenant_factory()["tenant_id"]
    with SessionLocal() as db:
        purchase = _purchase(db, tenant_id, PRODUCT_ACCESS_RENEWAL, "checkout-unpaid")
        purchase.status = "unpaid"
        db.flush()
        with pytest.raises(ValueError, match="Verified paid purchase required"):
            grant_v2_access_purchase(
                db, tenant_id=tenant_id, product_code=PRODUCT_ACCESS_RENEWAL,
                purchase_id=purchase.id,
            )



def test_late_validation_credit_consumption_never_extends_expired_v2_pass(tenant_factory):
    tenant_id = tenant_factory()["tenant_id"]
    with SessionLocal() as db:
        purchase = _purchase(db, tenant_id, PRODUCT_ACCESS_RENEWAL_VALIDATION, "checkout-late-validation")
        grant = grant_v2_access_purchase(
            db, tenant_id=tenant_id, product_code=PRODUCT_ACCESS_RENEWAL_VALIDATION,
            purchase_id=purchase.id,
        )
        now = datetime.now(timezone.utc)
        expired = now - timedelta(days=1)
        grant.valid_until_utc = expired
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        tenant.premium_until_utc = expired
        credit = db.query(TenantScanCredit).filter_by(
            tenant_id=tenant_id, source_purchase_id=purchase.id
        ).one()
        credit.status = "consumed"
        credit.consumed_at_utc = now
        db.flush()
        access = build_product_access_snapshot(db, tenant)
        assert not access["premium_active"]
        assert not access["validation_access_active"]
        db.commit()



def test_legacy_free_entry_is_permanently_visible_to_v2_tenant(tenant_factory, scan_factory):
    tenant_id = tenant_factory()["tenant_id"]
    scan_factory(tenant_id=tenant_id, scan_id="historic-free-entry")
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(ScanRunStatus(
            run_id="historic-free-entry", tenant_id=tenant_id,
            scan_mode="deep", status="completed",
            created_at_utc=now, updated_at_utc=now,
            completed_at_utc=now, result_persisted_at_utc=now,
        ))
        db.add(TenantScanCredit(
            tenant_id=tenant_id, product_code="free_entry",
            status="consumed", source="historical",
            consumed_scan_id="historic-free-entry",
            created_at_utc=now, consumed_at_utc=now,
        ))
        db.flush()
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        snap = build_product_access_snapshot(db, tenant)
        assert snap["free_access_permanent"]
        assert snap["has_completed_data_health_score"]
        assert is_original_free_scan(db, tenant_id, "historic-free-entry")
        assert not is_original_free_scan(db, tenant_id, "some_other_scan")
        db.commit()



def test_scan_credit_is_not_full_report_permission(tenant_factory):
    tenant_id = tenant_factory(plan="free", license_status="active")["tenant_id"]
    with SessionLocal() as db:
        now = datetime.now(timezone.utc)
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        db.add(TenantScanCredit(
            tenant_id=tenant_id, product_code="validation_check", status="available",
            source="renewal_validation_purchase",
            created_at_utc=now,
        ))
        db.flush()
        features = resolve_product_features(db, tenant)
        assert "deep_scan" in features
        assert "executive_report" not in features
        assert "recommendations" not in features
        assert "analytics_single_scan" not in features


def test_expired_v2_entitlement_does_not_resurrect_premium_features(tenant_factory):
    tenant_id = tenant_factory(plan="free", license_status="active")["tenant_id"]
    with SessionLocal() as db:
        now = datetime.now(timezone.utc)
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        db.add(TenantProductEntitlement(
            tenant_id=tenant_id, product_code=PRODUCT_ACCESS_RENEWAL,
            status="active", source="expired-test",
            valid_until_utc=now - timedelta(days=1),
            created_at_utc=now - timedelta(days=20), updated_at_utc=now,
        ))
        db.flush()
        features = resolve_product_features(db, tenant)
        assert "executive_report" not in features
        assert "analytics_single_scan" not in features



def test_only_first_of_multiple_historical_free_scans_is_permanently_visible(
    tenant_factory, scan_factory,
):
    tenant_id = tenant_factory()["tenant_id"]
    first_id, later_id = "original-free-legacy", "later-free-legacy"
    scan_factory(tenant_id=tenant_id, scan_id=first_id)
    scan_factory(tenant_id=tenant_id, scan_id=later_id)
    first_date = datetime(2026, 10, 1, tzinfo=timezone.utc)
    with SessionLocal() as db:
        for scan_id, date in ((first_id, first_date), (later_id, first_date + timedelta(days=2))):
            db.add(ScanRunStatus(
                run_id=scan_id, tenant_id=tenant_id, scan_mode="deep",
                status="completed", created_at_utc=date, updated_at_utc=date,
                completed_at_utc=date, result_persisted_at_utc=date,
            ))
            db.add(TenantScanCredit(
                tenant_id=tenant_id, product_code="free_entry",
                status="consumed", source="legacy",
                consumed_scan_id=scan_id, created_at_utc=date,
                consumed_at_utc=date,
            ))
        db.flush()
        assert is_original_free_scan(db, tenant_id, first_id)
        assert not is_original_free_scan(db, tenant_id, later_id)
