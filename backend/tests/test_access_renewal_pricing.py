"""V2 pricing must be explicitly configured before any paid checkout."""
from __future__ import annotations

from types import SimpleNamespace
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app.core.settings import settings
from app.db import SessionLocal
from app.models import ProductPricingMatrixConfig, Scan, ScanRunStatus
from app.routers.billing import _normalize_checkout_product_code, CheckoutSessionRequest
from app.services.product_license_service import (
    PRODUCT_ACCESS_RENEWAL,
    PRODUCT_ACCESS_RENEWAL_VALIDATION,
    PRODUCT_FULL_ASSESSMENT_V2,
)
from app.services.product_pricing_service import (
    get_matrix_price,
    resolve_checkout_matrix_price,
    build_public_pricing_summary,
    build_public_pricing_matrix,
    ProductPricingValidationError,
    ensure_default_product_pricing_matrix,
    PRODUCT_PRICING_MATRIX_DEFAULTS,
    PRICING_TIER_ORDER,
    V2_TIER_ORDER,
    V2_TIER_MAX_RECORDS,
)


NEW_CODES = (PRODUCT_FULL_ASSESSMENT_V2, PRODUCT_ACCESS_RENEWAL, PRODUCT_ACCESS_RENEWAL_VALIDATION)


@pytest.mark.parametrize("product_code", NEW_CODES)
def test_new_products_are_not_priced_or_active_without_explicit_configuration(product_code):
    with SessionLocal() as db:
        ensure_default_product_pricing_matrix(db)
        for tier in V2_TIER_ORDER:
            price = get_matrix_price(db, product_code, tier)
            assert price.amount_cents is None
            assert price.stripe_price_id is None
            assert price.is_active is False
            assert price.product_key == product_code
            assert price.max_records == V2_TIER_MAX_RECORDS[tier]
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
def test_v2_checkout_price_is_tier_specific_and_never_inherited_from_legacy(monkeypatch, product_code):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
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
            db, product_key=product_code, record_count=900_000,
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
    with SessionLocal() as db:
        now = datetime.now(timezone.utc)
        scan = db.query(Scan).filter_by(scan_id="v2-price-scan").one()
        scan.bc_company_id = "11111111-2222-3333-4444-555555555555"
        scan.lcy_code = "EUR"
        db.add(ScanRunStatus(
            tenant_id=tenant["tenant_id"], run_id=scan.scan_id,
            scan_mode="deep", status="completed", created_at_utc=now,
            updated_at_utc=now, completed_at_utc=now,
            result_persisted_at_utc=now,
        ))
        db.commit()
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


@pytest.mark.parametrize("count,tier", [
    (250_000, "starter"),
    (250_001, "professional"),
    (1_000_000, "professional"),
    (1_000_001, "business"),
    (5_000_000, "business"),
    (5_000_001, "enterprise"),
    (20_000_000, "enterprise"),
    (20_000_001, "custom"),
])
def test_v2_record_tier_boundaries(monkeypatch, count, tier):
    from app.services.product_license_service import pricing_tier_for_record_count
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    assert pricing_tier_for_record_count(count) == tier


def test_legacy_tier_boundaries_are_unchanged(monkeypatch):
    from app.services.product_license_service import pricing_tier_for_record_count
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", False)
    assert pricing_tier_for_record_count(100_000) == "starter"
    assert pricing_tier_for_record_count(100_001) == "professional"
    assert pricing_tier_for_record_count(250_001) == "business"
    assert pricing_tier_for_record_count(500_001) == "enterprise"


def test_large_custom_tenant_never_uses_legacy_monitoring_starter_price(monkeypatch):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    with SessionLocal() as db:
        price = resolve_checkout_matrix_price(
            db, product_key="monitoring_monthly", record_count=20_000_001,
            env_price_id="price_monitoring_starter",
        )
        assert price.pricing_tier == "custom"
        assert price.contact_sales is True
        assert price.stripe_price_id is None
        assert price.is_active is False


@pytest.mark.parametrize("product_code", NEW_CODES)
def test_unverified_record_count_is_rejected_for_new_paid_products(monkeypatch, product_code):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    with SessionLocal() as db:
        with pytest.raises(ProductPricingValidationError, match="record count"):
            resolve_checkout_matrix_price(db, product_key=product_code, record_count=None)


def test_public_v2_pricing_does_not_advertise_legacy_one_time_products(monkeypatch):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    with SessionLocal() as db:
        summary = build_public_pricing_summary(db)
        matrix = build_public_pricing_matrix(db)
        published = {item["product_key"] for item in summary}
        assert "full_analysis" not in published
        assert "validation_check" not in published
        assert not any(item["product_key"] in {"full_analysis", "validation_check"} for item in matrix)
        assert not published.intersection(NEW_CODES)


def test_public_v2_pricing_shows_only_explicitly_activated_renewal_product(monkeypatch):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    with SessionLocal() as db:
        ensure_default_product_pricing_matrix(db)
        row = db.query(ProductPricingMatrixConfig).filter_by(
            product_key=PRODUCT_ACCESS_RENEWAL, pricing_tier="starter"
        ).one()
        row.amount_cents, row.stripe_price_id, row.is_active = 7900, "price_approved_renewal", True
        db.commit()
        summary = build_public_pricing_summary(db)
        renewal = [item for item in summary if item["product_key"] == PRODUCT_ACCESS_RENEWAL]
        assert len(renewal) == 1
        assert renewal[0]["price_cents"] == 7900
        assert PRODUCT_FULL_ASSESSMENT_V2 not in {item["product_key"] for item in summary}
        assert PRODUCT_ACCESS_RENEWAL_VALIDATION not in {item["product_key"] for item in summary}



def test_verified_v2_record_count_ignores_pending_scan_and_uses_largest_persisted(tenant_factory, deep_scan_factory):
    from app.services.product_license_service import verified_pricing_record_count
    t = tenant_factory()
    deep_scan_factory(tenant_id=t["tenant_id"], scan_id="pricing-complete", total_records=300_000)
    deep_scan_factory(tenant_id=t["tenant_id"], scan_id="pricing-pending", total_records=10)
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        for scan in db.query(Scan).filter(Scan.tenant_id == t["tenant_id"]):
            scan.bc_company_id = "11111111-2222-3333-4444-555555555555"
        db.add(ScanRunStatus(
            tenant_id=t["tenant_id"], run_id="pricing-complete", scan_mode="deep",
            status="completed", created_at_utc=now, updated_at_utc=now,
            completed_at_utc=now, result_persisted_at_utc=now,
        ))
        db.commit()
        assert verified_pricing_record_count(db, t["tenant_id"]) == 300_000
        assert verified_pricing_record_count(db, "unknown-tenant") is None
