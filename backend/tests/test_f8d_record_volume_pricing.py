import pytest

from app.services.product_license_service import PRODUCT_ASSESSMENT, PRODUCT_VALIDATION_CHECK
from app.services.quick_assessment_access_service import PRODUCT_QUICK_ASSESSMENT
from app.services.record_volume_pricing_service import (
    CHANNEL_FIVERR,
    RECORD_VOLUME_CLASSES,
    RECORD_VOLUME_PRICING_METRIC,
    RECORD_VOLUME_PRICING_MODEL,
    fiverr_price_recommendation,
    fiverr_price_recommendations,
    legacy_direct_tier_code_for_count,
    normalize_record_count,
    record_volume_class_for_count,
)


def test_canonical_record_volume_boundaries_are_exact():
    cases = [
        (-1, "micro"),
        (0, "micro"),
        (100_000, "micro"),
        (100_001, "small"),
        (250_000, "small"),
        (250_001, "medium"),
        (1_000_000, "medium"),
        (1_000_001, "large"),
        (5_000_000, "large"),
        (5_000_001, "enterprise"),
        (20_000_000, "enterprise"),
        (20_000_001, "custom"),
        (99_000_000, "custom"),
    ]
    for count, expected in cases:
        assert record_volume_class_for_count(count)["code"] == expected

    assert [row["code"] for row in RECORD_VOLUME_CLASSES] == [
        "micro",
        "small",
        "medium",
        "large",
        "enterprise",
        "custom",
    ]


def test_record_count_normalization_is_safe_and_non_negative():
    assert normalize_record_count(None) == 0
    assert normalize_record_count(-10) == 0
    assert normalize_record_count("100001") == 100_001
    assert normalize_record_count("not-a-number") == 0


@pytest.mark.parametrize(
    ("record_count", "quick", "assessment", "validation"),
    [
        (100_000, 129.0, 299.0, 149.0),
        (100_001, 169.0, 349.0, 179.0),
        (250_001, 229.0, 449.0, 229.0),
        (1_000_001, 349.0, 649.0, 329.0),
    ],
)
def test_fiverr_fixed_price_matrix(record_count, quick, assessment, validation):
    bundle = fiverr_price_recommendations(record_count)
    assert bundle["pricing_model"] == RECORD_VOLUME_PRICING_MODEL
    assert bundle["pricing_metric"] == RECORD_VOLUME_PRICING_METRIC
    assert bundle["channel"] == CHANNEL_FIVERR
    assert bundle["currency"] == "USD"
    assert bundle["record_count"] == record_count

    expected = {
        PRODUCT_QUICK_ASSESSMENT: quick,
        PRODUCT_ASSESSMENT: assessment,
        PRODUCT_VALIDATION_CHECK: validation,
    }
    for product_code, price in expected.items():
        quote = bundle["products"][product_code]
        assert quote["price"] == price
        assert quote["price_cents"] == int(price * 100)
        assert quote["custom_offer_required"] is False
        assert quote["recommendation_type"] == "fixed_price"


def test_fiverr_enterprise_requires_custom_offer_and_custom_requires_review():
    enterprise = fiverr_price_recommendations(5_000_001)
    assert enterprise["record_class"]["code"] == "enterprise"
    for quote in enterprise["products"].values():
        assert quote["price"] is None
        assert quote["price_cents"] is None
        assert quote["custom_offer_required"] is True
        assert quote["recommendation_type"] == "custom_offer"

    custom = fiverr_price_recommendations(20_000_001)
    assert custom["record_class"]["code"] == "custom"
    for quote in custom["products"].values():
        assert quote["price"] is None
        assert quote["price_cents"] is None
        assert quote["custom_offer_required"] is True
        assert quote["recommendation_type"] == "individual_review"


def test_single_product_quote_is_channel_metadata_only():
    quote = fiverr_price_recommendation(
        total_records=90_000,
        product_code=PRODUCT_QUICK_ASSESSMENT,
    )
    assert quote == {
        "pricing_model": RECORD_VOLUME_PRICING_MODEL,
        "pricing_metric": RECORD_VOLUME_PRICING_METRIC,
        "channel": "fiverr",
        "currency": "USD",
        "record_count": 90_000,
        "record_class": {
            "code": "micro",
            "display_name": "Micro",
            "min_records": 0,
            "max_records": 100_000,
        },
        "product_code": PRODUCT_QUICK_ASSESSMENT,
        "price_cents": 12_900,
        "price": 129.0,
        "custom_offer_required": False,
        "recommendation_type": "fixed_price",
    }


def test_unsupported_fiverr_product_is_rejected():
    with pytest.raises(ValueError, match="Unsupported Fiverr pricing product"):
        fiverr_price_recommendation(total_records=100, product_code="monitoring_monthly")


def test_legacy_direct_pricing_bridge_preserves_existing_eur_tier_contract():
    assert legacy_direct_tier_code_for_count(0) == "small"
    assert legacy_direct_tier_code_for_count(100_000) == "small"
    assert legacy_direct_tier_code_for_count(100_001) == "small"
    assert legacy_direct_tier_code_for_count(250_000) == "small"
    assert legacy_direct_tier_code_for_count(250_001) == "medium"
    assert legacy_direct_tier_code_for_count(1_000_001) == "large"
    assert legacy_direct_tier_code_for_count(5_000_001) == "enterprise"
    assert legacy_direct_tier_code_for_count(20_000_001) == "enterprise_plus"
