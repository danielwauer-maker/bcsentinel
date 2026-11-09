"""Database-level regression for Full 14d and Renewal checkout grant semantics."""
from datetime import datetime, timedelta, timezone

import pytest

from app.core.settings import settings
from app.db import SessionLocal
from app.models import Tenant, TenantProductEntitlement, TenantScanCredit
from app.services.product_license_service import (
    PRODUCT_FULL_ASSESSMENT_V2,
    PRODUCT_ACCESS_RENEWAL,
    PRODUCT_ACCESS_RENEWAL_VALIDATION,
    grant_v2_access_purchase,
    record_product_purchase,
    build_product_access_snapshot,
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
