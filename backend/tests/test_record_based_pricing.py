import inspect
from pathlib import Path

from app.services.impact_service import calculate_scan_commercials
from app.services.product_license_service import (
    PRODUCT_ASSESSMENT,
    PRODUCT_MONITORING_ANNUAL,
    PRODUCT_MONITORING_MONTHLY,
    PRODUCT_VALIDATION_CHECK,
)
from app.services.product_pricing_service import (
    DEFAULT_TIER_PRICES_CENTS,
    PRICING_METRIC,
    PRICING_MODEL,
    STRIPE_SYNC_WARNING,
    pricing_sku_key,
    tier_for_record_count,
)


def test_pricing_model_and_metric_are_canonical():
    assert PRICING_MODEL == "record_volume_tiers"
    assert PRICING_METRIC == "bcsentinel_analyzed_record_volume"
    assert "Stripe" in STRIPE_SYNC_WARNING


def test_arv_tier_boundaries():
    assert tier_for_record_count(0)["code"] == "small"
    assert tier_for_record_count(250_000)["code"] == "small"
    assert tier_for_record_count(250_001)["code"] == "medium"
    assert tier_for_record_count(1_000_000)["code"] == "medium"
    assert tier_for_record_count(1_000_001)["code"] == "large"
    assert tier_for_record_count(5_000_000)["code"] == "large"
    assert tier_for_record_count(5_000_001)["code"] == "enterprise"
    assert tier_for_record_count(20_000_000)["code"] == "enterprise"
    assert tier_for_record_count(20_000_001)["code"] == "enterprise_plus"


def test_default_tier_prices():
    expected = {
        "small": (24_900, 12_900, 19_900, 199_000),
        "medium": (39_900, 19_900, 29_900, 299_000),
        "large": (69_900, 34_900, 49_900, 499_000),
        "enterprise": (119_000, 59_000, 79_900, 799_000),
    }
    for tier, values in expected.items():
        prices = DEFAULT_TIER_PRICES_CENTS[tier]
        assert (
            prices[PRODUCT_ASSESSMENT],
            prices[PRODUCT_VALIDATION_CHECK],
            prices[PRODUCT_MONITORING_MONTHLY],
            prices[PRODUCT_MONITORING_ANNUAL],
        ) == values


def test_enterprise_plus_is_custom_quote_only():
    assert all(value is None for value in DEFAULT_TIER_PRICES_CENTS["enterprise_plus"].values())


def test_runtime_sku_keys_are_tier_specific():
    assert pricing_sku_key("small", PRODUCT_ASSESSMENT) == "small__assessment"
    assert pricing_sku_key("enterprise", PRODUCT_MONITORING_ANNUAL) == "enterprise__monitoring_annual"


def test_scan_commercials_pass_arv_into_monitoring_price_resolution():
    source = inspect.getsource(calculate_scan_commercials)
    assert "build_monitoring_pricing_breakdown(db, record_count=total_records)" in source


def test_admin_pricing_screen_warns_about_stripe_sync():
    template = (Path(__file__).parents[1] / "app" / "templates" / "admin_tenants.html").read_text(encoding="utf-8")
    assert "Eine Änderung hier aktualisiert Stripe-Price-Objekte nicht automatisch." in template
    assert "Stripe-Preise und Price-ID-Zuordnungen müssen beim Zahlungsdienstleister ebenfalls korrekt geändert" in template
    assert "blockiert produktiven Checkout" in template
