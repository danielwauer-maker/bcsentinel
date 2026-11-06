from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace

from app.db import SessionLocal
from app.services.commercial_checkout_service import commercial_quote, create_stripe_override_coupon, get_active_pilot_sponsorship
from app.services.product_license_service import PRODUCT_MONITORING_MONTHLY, utc_now
from app.services.tenant_commercial_service import create_commercial_override, grant_pilot_sponsorship


def test_sponsored_pilot_is_resolved_without_stripe(tenant_factory):
    tenant = tenant_factory(); now = utc_now()
    with SessionLocal() as db:
        grant_pilot_sponsorship(db, tenant_id=tenant["tenant_id"], product_code=PRODUCT_MONITORING_MONTHLY,
                                valid_from_utc=now - timedelta(minutes=1), valid_until_utc=now + timedelta(days=45),
                                actor="pytest", reason="Controlled pilot")
        db.commit()
        quote = commercial_quote(db, tenant_id=tenant["tenant_id"], product_code=PRODUCT_MONITORING_MONTHLY, list_price_cents=29_900)
    assert quote["pilot_sponsorship_active"] is True


def test_list_price_without_override_allows_promotion_code(tenant_factory):
    tenant = tenant_factory()
    with SessionLocal() as db:
        quote = commercial_quote(db, tenant_id=tenant["tenant_id"], product_code="assessment", list_price_cents=39_900)
    assert quote["effective_price_cents"] == 39_900
    assert quote["promotion_code_allowed"] is True


def test_tenant_override_creates_single_use_stripe_coupon(monkeypatch, tenant_factory):
    tenant = tenant_factory(); now = utc_now(); captured = {}
    class FakeCoupon:
        @staticmethod
        def create(**kwargs):
            captured.update(kwargs); return SimpleNamespace(id="coupon_test")
    monkeypatch.setattr("app.services.commercial_checkout_service.stripe.Coupon", FakeCoupon)
    with SessionLocal() as db:
        override = create_commercial_override(db, tenant_id=tenant["tenant_id"], product_code="assessment",
                                              override_type="fixed_price", value_number=99.0,
                                              valid_from_utc=now - timedelta(minutes=1), valid_until_utc=now + timedelta(days=10),
                                              actor="pytest")
        db.flush()
        coupon_id = create_stripe_override_coupon(override=override, list_price_cents=39_900,
                                                  effective_price_cents=9_900, product_code="assessment")
    assert coupon_id == "coupon_test"
    assert captured["amount_off"] == 30_000
    assert captured["duration"] == "once"
    assert captured["max_redemptions"] == 1


def test_recurring_override_coupon_has_bounded_duration(monkeypatch, tenant_factory):
    tenant = tenant_factory(); now = utc_now(); captured = {}
    class FakeCoupon:
        @staticmethod
        def create(**kwargs):
            captured.update(kwargs); return SimpleNamespace(id="coupon_recurring")
    monkeypatch.setattr("app.services.commercial_checkout_service.stripe.Coupon", FakeCoupon)
    with SessionLocal() as db:
        override = create_commercial_override(db, tenant_id=tenant["tenant_id"], product_code=PRODUCT_MONITORING_MONTHLY,
                                              override_type="percent_discount", value_number=50,
                                              valid_from_utc=now - timedelta(minutes=1), valid_until_utc=now + timedelta(days=90),
                                              actor="pytest")
        db.flush()
        create_stripe_override_coupon(override=override, list_price_cents=29_900, effective_price_cents=14_950,
                                      product_code=PRODUCT_MONITORING_MONTHLY)
    assert captured["duration"] == "repeating"
    assert 1 <= captured["duration_in_months"] <= 36


def test_expired_sponsorship_is_not_active(tenant_factory):
    tenant = tenant_factory(); now = utc_now()
    with SessionLocal() as db:
        sponsorship = grant_pilot_sponsorship(db, tenant_id=tenant["tenant_id"], product_code=PRODUCT_MONITORING_MONTHLY,
                                              valid_from_utc=now - timedelta(days=10), valid_until_utc=now - timedelta(days=1),
                                              actor="pytest", reason="Expired pilot")
        sponsorship.status = "active"; db.commit()
        assert get_active_pilot_sponsorship(db, tenant_id=tenant["tenant_id"], product_code=PRODUCT_MONITORING_MONTHLY) is None
