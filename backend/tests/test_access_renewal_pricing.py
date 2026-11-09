"""V2 pricing must be explicitly configured before any paid checkout."""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.core.settings import settings
from app.db import SessionLocal
from app.models import ProductPricingMatrixConfig
from app.routers.billing import _normalize_checkout_product_code, CheckoutSessionRequest
from app.services.product_license_service import (
    PRODUCT_ACCESS_RENEWAL,
    PRODUCT_ACCESS_RENEWAL_VALIDATION,
    PRODUCT_FULL_ASSESSMENT_V2,
)
from app.services.product_pricing_service import (
    get_matrix_price,
    resolve_checkout_matrix_price,
    ensure_default_product_pricing_matrix,
    PRODUCT_PRICING_MATRIX_DEFAULTS,
    PRICING_TIER_ORDER,
)


NEW_CODES = (PRODUCT_FULL_ASSESSMENT_V2, PRODUCT_ACCESS_RENEWAL, PRODUCT_ACCESS_RENEWAL_VALIDATION)


@pytest.mark.parametrize("product_code", NEW_CODES)
def test_new_products_are_not_priced_or_active_without_explicit_configuration(product_code):
    with SessionLocal() as db:
        ensure_default_product_pricing_matrix(db)
        for tier in PRICING_TIER_ORDER:
            price = get_matrix_price(db, product_code, tier)
            assert price.amount_cents is None
            assert price.stripe_price_id is None
            assert price.is_active is False
            assert price.product_key == product_code
            assert product_code in PRODUCT_PRICING_MATRIX_DEFAULTS


@pytest.mark.parametrize("product_code", NEW_CODES)
def test_checkout_rejects_direct_v2_products_when_rollout_off(monkeypatch, product_code):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", False)
    with pytest.raises(HTTPException) as exc:
        _normalize_checkout_product_code(CheckoutSessionRequest(tenant_id="tenant_test", product_code=product_code))
    assert exc.value.status_code == 400


@pytest.mark.parametrize("old_code,new_code", [
    ("full_analysis", PRODUCT_FULL_ASSESSMENT_V2),
    ("validation_check", PRODUCT_ACCESS_RENEWAL_VALIDATION),
])
def test_new_checkout_maps_legacy_buttons_without_modifying_historical_purchases(monkeypatch, old_code, new_code):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    result = _normalize_checkout_product_code(CheckoutSessionRequest(tenant_id="tenant_test", product_code=old_code))
    assert result == new_code


def test_legacy_checkout_still_uses_original_product_when_rollout_off(monkeypatch):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", False)
    for product_code in ("full_analysis", "validation_check"):
        result = _normalize_checkout_product_code(
            CheckoutSessionRequest(tenant_id="tenant_test", product_code=product_code)
        )
        assert result == product_code



@pytest.mark.parametrize("product_code", NEW_CODES)
def test_v2_checkout_price_is_tier_specific_and_never_inherited_from_legacy(product_code):
    with SessionLocal() as db:
        ensure_default_product_pricing_matrix(db)
        starter = db.query(ProductPricingMatrixConfig).filter_by(
            product_key=product_code, pricing_tier="starter"
        ).one()
        starter.amount_cents = 8700
        starter.stripe_price_id = "price_v2_explicit_starter"
        starter.billing_interval = "one_time"
        starter.is_active = True
        db.commit()

        configured = resolve_checkout_matrix_price(
            db, product_key=product_code, record_count=10_000,
            env_price_id="price_fallback_must_not_override_row",
        )
        assert configured.amount_cents == 8700
        assert configured.stripe_price_id == "price_v2_explicit_starter"
        assert configured.is_active is True
        assert configured.contact_sales is False

        other_tier = resolve_checkout_matrix_price(
            db, product_key=product_code, record_count=200_000,
            env_price_id="price_v2_explicit_starter",
        )
        assert other_tier.pricing_tier == "professional"
        assert other_tier.amount_cents is None
        assert other_tier.is_active is False
        assert other_tier.contact_sales is True



@pytest.mark.parametrize("product_code,requires_prior_purchase", [
    (PRODUCT_FULL_ASSESSMENT_V2, False),
    (PRODUCT_ACCESS_RENEWAL, True),
    (PRODUCT_ACCESS_RENEWAL_VALIDATION, True),
])
def test_v2_checkout_uses_its_own_stripe_price_and_product_metadata(
    client, monkeypatch, tenant_factory, auth_header_factory, deep_scan_factory,
    product_code, requires_prior_purchase,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    deep_scan_factory(tenant_id=tenant["tenant_id"], scan_id="v2-price-scan", total_records=8500)
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "sk_test")
    monkeypatch.setattr(settings, "APP_BASE_URL", "https://app.example.com")
    monkeypatch.setattr(
        "app.routers.billing.build_product_access_snapshot",
        lambda db, t: {
            "monitoring_active": False,
            "has_completed_data_health_score": True,
            "premium_active": False,
            "full_analysis_access_active": False,
            "validation_check_access_active": False,
        },
    )
    with SessionLocal() as db:
        ensure_default_product_pricing_matrix(db)
        row = db.query(ProductPricingMatrixConfig).filter_by(
            product_key=product_code, pricing_tier="starter"
        ).one()
        row.amount_cents = 8900
        row.stripe_price_id = "price_" + product_code
        row.is_active = True
        if requires_prior_purchase:
            from app.services.product_license_service import record_product_purchase
            record_product_purchase(
                db, tenant_id=tenant["tenant_id"], product_code=PRODUCT_FULL_ASSESSMENT_V2,
                provider="test", provider_checkout_session_id="old_full_purchase",
                provider_payment_intent_id=None, status="paid", currency="EUR",
                amount_total=249.0,
            )
        db.commit()

    sent = {}
    def mock_stripe_create(**kwargs):
        sent.update(kwargs)
        return SimpleNamespace(id="cs_test_v2_checkout", url="https://stripe.example/v2")

    monkeypatch.setattr("app.routers.billing.stripe.checkout.Session.create", mock_stripe_create)
    response = client.post(
        "/billing/checkout/session",
        headers=auth_header_factory(tenant),
        json={"tenant_id": tenant["tenant_id"], "product_code": product_code},
    )
    assert response.status_code == 200, response.text
    assert sent["mode"] == "payment"
    assert sent["line_items"] == [{"price": "price_" + product_code, "quantity": 1}]
    assert sent["metadata"]["product_code"] == product_code
