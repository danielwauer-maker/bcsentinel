from __future__ import annotations

from typing import Any

from app.services.product_license_service import (
    PRODUCT_ASSESSMENT,
    PRODUCT_VALIDATION_CHECK,
)
from app.services.quick_assessment_access_service import PRODUCT_QUICK_ASSESSMENT


RECORD_VOLUME_PRICING_MODEL = "canonical_record_volume_classes_v1"
RECORD_VOLUME_PRICING_METRIC = "bcsentinel_analyzed_record_volume"
CHANNEL_FIVERR = "fiverr"

# Canonical sizing taxonomy shared by commercial channels and operator tooling.
# Boundaries are intentionally independent from the legacy/direct EUR pricing
# tier keys in product_pricing_service.py so the existing Stripe/direct pricing
# contract can remain backward compatible while F8 rolls out progressively.
RECORD_VOLUME_CLASSES = (
    {"code": "micro", "display_name": "Micro", "min_records": 0, "max_records": 100_000},
    {"code": "small", "display_name": "Small", "min_records": 100_001, "max_records": 250_000},
    {"code": "medium", "display_name": "Medium", "min_records": 250_001, "max_records": 1_000_000},
    {"code": "large", "display_name": "Large", "min_records": 1_000_001, "max_records": 5_000_000},
    {"code": "enterprise", "display_name": "Enterprise", "min_records": 5_000_001, "max_records": 20_000_000},
    {"code": "custom", "display_name": "Custom", "min_records": 20_000_001, "max_records": None},
)

# Fiverr pilot pricing is sales-channel metadata only. It does not grant
# entitlements and does not alter the existing direct/Stripe EUR price table.
# None means the operator must create a Custom Offer / perform individual review.
FIVERR_TARGET_PRICES_USD_CENTS: dict[str, dict[str, int | None]] = {
    "micro": {
        PRODUCT_QUICK_ASSESSMENT: 12_900,
        PRODUCT_ASSESSMENT: 29_900,
        PRODUCT_VALIDATION_CHECK: 14_900,
    },
    "small": {
        PRODUCT_QUICK_ASSESSMENT: 16_900,
        PRODUCT_ASSESSMENT: 34_900,
        PRODUCT_VALIDATION_CHECK: 17_900,
    },
    "medium": {
        PRODUCT_QUICK_ASSESSMENT: 22_900,
        PRODUCT_ASSESSMENT: 44_900,
        PRODUCT_VALIDATION_CHECK: 22_900,
    },
    "large": {
        PRODUCT_QUICK_ASSESSMENT: 34_900,
        PRODUCT_ASSESSMENT: 64_900,
        PRODUCT_VALIDATION_CHECK: 32_900,
    },
    "enterprise": {
        PRODUCT_QUICK_ASSESSMENT: None,
        PRODUCT_ASSESSMENT: None,
        PRODUCT_VALIDATION_CHECK: None,
    },
    "custom": {
        PRODUCT_QUICK_ASSESSMENT: None,
        PRODUCT_ASSESSMENT: None,
        PRODUCT_VALIDATION_CHECK: None,
    },
}

FIVERR_PRICED_PRODUCTS = (
    PRODUCT_QUICK_ASSESSMENT,
    PRODUCT_ASSESSMENT,
    PRODUCT_VALIDATION_CHECK,
)


def normalize_record_count(total_records: int | float | str | None) -> int:
    """Normalize authoritative analyzed volume without accepting negatives."""
    try:
        value = int(total_records or 0)
    except (TypeError, ValueError):
        value = 0
    return max(value, 0)


def record_volume_class_for_count(total_records: int | float | str | None) -> dict[str, Any]:
    record_count = normalize_record_count(total_records)
    for row in RECORD_VOLUME_CLASSES:
        max_records = row["max_records"]
        if record_count >= int(row["min_records"]) and (
            max_records is None or record_count <= int(max_records)
        ):
            return dict(row)
    return dict(RECORD_VOLUME_CLASSES[-1])


def _normalize_product_code(product_code: str) -> str:
    normalized = str(product_code or "").strip().lower()
    if normalized not in FIVERR_PRICED_PRODUCTS:
        raise ValueError(f"Unsupported Fiverr pricing product: {product_code}")
    return normalized


def fiverr_price_recommendation(
    *,
    total_records: int | float | str | None,
    product_code: str,
) -> dict[str, Any]:
    """Return the canonical Fiverr pilot recommendation for one paid product.

    This is deliberately a read model only. It never grants an entitlement,
    creates a scan credit, records a purchase or redirects a payment flow.
    """
    record_count = normalize_record_count(total_records)
    volume_class = record_volume_class_for_count(record_count)
    normalized_product = _normalize_product_code(product_code)
    price_cents = FIVERR_TARGET_PRICES_USD_CENTS[volume_class["code"]][normalized_product]
    custom_offer_required = price_cents is None

    return {
        "pricing_model": RECORD_VOLUME_PRICING_MODEL,
        "pricing_metric": RECORD_VOLUME_PRICING_METRIC,
        "channel": CHANNEL_FIVERR,
        "currency": "USD",
        "record_count": record_count,
        "record_class": volume_class,
        "product_code": normalized_product,
        "price_cents": price_cents,
        "price": None if price_cents is None else round(price_cents / 100, 2),
        "custom_offer_required": custom_offer_required,
        "recommendation_type": (
            "individual_review"
            if volume_class["code"] == "custom"
            else ("custom_offer" if custom_offer_required else "fixed_price")
        ),
    }


def fiverr_price_recommendations(total_records: int | float | str | None) -> dict[str, Any]:
    """Return one reusable read model for Quick, Full Assessment and Validation."""
    record_count = normalize_record_count(total_records)
    volume_class = record_volume_class_for_count(record_count)
    products = {
        product_code: fiverr_price_recommendation(
            total_records=record_count,
            product_code=product_code,
        )
        for product_code in FIVERR_PRICED_PRODUCTS
    }
    return {
        "pricing_model": RECORD_VOLUME_PRICING_MODEL,
        "pricing_metric": RECORD_VOLUME_PRICING_METRIC,
        "channel": CHANNEL_FIVERR,
        "currency": "USD",
        "record_count": record_count,
        "record_class": volume_class,
        "products": products,
    }


def legacy_direct_tier_code_for_count(total_records: int | float | str | None) -> str:
    """Bridge F8 canonical sizing to the currently deployed direct EUR tiers.

    Micro and Small intentionally map to the existing <=250k direct tier. This
    preserves current public/Stripe EUR behavior until that channel is migrated
    explicitly, while all new channel-aware code can already use the canonical
    six-class taxonomy.
    """
    class_code = record_volume_class_for_count(total_records)["code"]
    return {
        "micro": "small",
        "small": "small",
        "medium": "medium",
        "large": "large",
        "enterprise": "enterprise",
        "custom": "enterprise_plus",
    }[class_code]
