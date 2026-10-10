from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace

from app.db import SessionLocal
from app.services.product_license_service import PRODUCT_MONITORING_MONTHLY, utc_now
from app.services.tenant_commercial_service import create_commercial_override, grant_pilot_sponsorship


def test_sponsored_pilot_commercial_checkout_skips_stripe_entirely(
    client,
    tenant_factory,
    auth_header_factory,
    deep_scan_factory,
    settings_state,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    deep_scan_factory(tenant_id=tenant["tenant_id"], scan_id="e4_sponsored", total_records=5_000)
    now = utc_now()
    with SessionLocal() as db:
        grant_pilot_sponsorship(
            db,
            tenant_id=tenant["tenant_id"],
            product_code=PRODUCT_MONITORING_MONTHLY,
            valid_from_utc=now - timedelta(minutes=1),
            valid_until_utc=now + timedelta(days=30),
            actor="pytest",
            reason="E4 controlled pilot",
        )
        db.commit()

    # A sponsored pilot is an internal commercial entitlement path and must not
    # depend on a fake EUR 0 Stripe checkout or even a configured Stripe key.
    settings_state(STRIPE_SECRET_KEY=None)
    response = client.post(
        "/billing/checkout/commercial-session",
        headers=auth_header_factory(tenant),
        json={"tenant_id": tenant["tenant_id"], "product_code": "monitoring_monthly"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["sponsored"] is True
    assert body["effective_price_cents"] == 0
    assert body["checkout_required"] is False
    assert body["promotion_code_allowed"] is False
    assert body["checkout_session_id"] is None
    assert body["provider"] is None


def test_list_price_commercial_checkout_allows_stripe_promotion_codes(
    client,
    tenant_factory,
    auth_header_factory,
    deep_scan_factory,
    settings_state,
    monkeypatch,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    deep_scan_factory(tenant_id=tenant["tenant_id"], scan_id="e4_list", total_records=5_000)
    settings_state(
        STRIPE_SECRET_KEY="sk_test",
        STRIPE_PRICE_ID_ASSESSMENT="price_assessment_small",
        BILLING_SUCCESS_URL="https://app.example.com/billing/success?session_id={CHECKOUT_SESSION_ID}",
        BILLING_CANCEL_URL="https://app.example.com/billing/cancel",
    )
    captured: dict = {}
    monkeypatch.setattr("app.routers.commercial_billing._verify_stripe_price_matches_quote", lambda *args, **kwargs: None)

    def fake_create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(id="cs_e4_list", url="https://stripe.example/e4-list")

    monkeypatch.setattr("app.routers.commercial_billing.stripe.checkout.Session.create", fake_create)
    response = client.post(
        "/billing/checkout/commercial-session",
        headers=auth_header_factory(tenant),
        json={"tenant_id": tenant["tenant_id"], "product_code": "assessment"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["list_price_cents"] == 24_900
    assert body["effective_price_cents"] == 24_900
    assert body["price_source"] == "list_price"
    assert body["promotion_code_allowed"] is True
    assert body["checkout_required"] is True
    assert captured["allow_promotion_codes"] is True
    assert "discounts" not in captured


def test_tenant_override_uses_one_controlled_discount_and_disables_stacking(
    client,
    tenant_factory,
    auth_header_factory,
    deep_scan_factory,
    settings_state,
    monkeypatch,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    deep_scan_factory(tenant_id=tenant["tenant_id"], scan_id="e4_override", total_records=5_000)
    now = utc_now()
    with SessionLocal() as db:
        create_commercial_override(
            db,
            tenant_id=tenant["tenant_id"],
            product_code="assessment",
            override_type="fixed_price",
            value_number=99.0,
            valid_from_utc=now - timedelta(minutes=1),
            valid_until_utc=now + timedelta(days=14),
            actor="pytest",
        )
        db.commit()

    settings_state(
        STRIPE_SECRET_KEY="sk_test",
        STRIPE_PRICE_ID_ASSESSMENT="price_assessment_small",
        BILLING_SUCCESS_URL="https://app.example.com/billing/success?session_id={CHECKOUT_SESSION_ID}",
        BILLING_CANCEL_URL="https://app.example.com/billing/cancel",
    )
    captured: dict = {}
    monkeypatch.setattr("app.routers.commercial_billing._verify_stripe_price_matches_quote", lambda *args, **kwargs: None)
    monkeypatch.setattr("app.routers.commercial_billing.create_stripe_override_coupon", lambda **kwargs: "coupon_e4_override")

    def fake_create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(id="cs_e4_override", url="https://stripe.example/e4-override")

    monkeypatch.setattr("app.routers.commercial_billing.stripe.checkout.Session.create", fake_create)
    response = client.post(
        "/billing/checkout/commercial-session",
        headers=auth_header_factory(tenant),
        json={"tenant_id": tenant["tenant_id"], "product_code": "assessment"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["list_price_cents"] == 24_900
    assert body["effective_price_cents"] == 9_900
    assert body["promotion_code_allowed"] is False
    assert captured["discounts"] == [{"coupon": "coupon_e4_override"}]
    assert "allow_promotion_codes" not in captured
