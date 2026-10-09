from __future__ import annotations

from typing import Any

from sqlalchemy import select

from app.models import ProductPricingConfig
from app.services.billing_service import utc_now
from app.services.product_license_service import (
    PRODUCT_ASSESSMENT,
    PRODUCT_MONITORING_ANNUAL,
    PRODUCT_MONITORING_MONTHLY,
    PRODUCT_VALIDATION_CHECK,
)

PRODUCT_BILLING_INTERVAL_ONE_TIME = "one_time"
PRODUCT_BILLING_INTERVAL_MONTH = "month"
PRODUCT_BILLING_INTERVAL_YEAR = "year"

PRICING_MODEL = "record_volume_tiers"
PRICING_METRIC = "bcsentinel_analyzed_record_volume"
STRIPE_SYNC_WARNING = (
    "Aenderungen an BCSentinel-Preisen aktualisieren Stripe-Price-Objekte nicht automatisch. "
    "Vor produktivem Checkout muessen die entsprechenden Stripe-Preise und Price-ID-Zuordnungen "
    "angepasst und verifiziert werden."
)

VOLUME_TIERS: tuple[dict[str, Any], ...] = (
    {"code": "small", "display_name": "Small", "min_records": 0, "max_records": 250_000},
    {"code": "medium", "display_name": "Medium", "min_records": 250_001, "max_records": 1_000_000},
    {"code": "large", "display_name": "Large", "min_records": 1_000_001, "max_records": 5_000_000},
    {"code": "enterprise", "display_name": "Enterprise", "min_records": 5_000_001, "max_records": 20_000_000},
    {"code": "enterprise_plus", "display_name": "Enterprise+", "min_records": 20_000_001, "max_records": None},
)

PRODUCT_DEFINITIONS: dict[str, dict[str, Any]] = {
    PRODUCT_ASSESSMENT: {
        "display_name": "Assessment",
        "billing_interval": PRODUCT_BILLING_INTERVAL_ONE_TIME,
    },
    PRODUCT_VALIDATION_CHECK: {
        "display_name": "Validation Check",
        "billing_interval": PRODUCT_BILLING_INTERVAL_ONE_TIME,
    },
    PRODUCT_MONITORING_MONTHLY: {
        "display_name": "Monitoring Monthly",
        "billing_interval": PRODUCT_BILLING_INTERVAL_MONTH,
    },
    PRODUCT_MONITORING_ANNUAL: {
        "display_name": "Monitoring Annual",
        "billing_interval": PRODUCT_BILLING_INTERVAL_YEAR,
    },
}

DEFAULT_TIER_PRICES_CENTS: dict[str, dict[str, int | None]] = {
    "small": {
        PRODUCT_ASSESSMENT: 24_900,
        PRODUCT_VALIDATION_CHECK: 12_900,
        PRODUCT_MONITORING_MONTHLY: 19_900,
        PRODUCT_MONITORING_ANNUAL: 199_000,
    },
    "medium": {
        PRODUCT_ASSESSMENT: 39_900,
        PRODUCT_VALIDATION_CHECK: 19_900,
        PRODUCT_MONITORING_MONTHLY: 29_900,
        PRODUCT_MONITORING_ANNUAL: 299_000,
    },
    "large": {
        PRODUCT_ASSESSMENT: 69_900,
        PRODUCT_VALIDATION_CHECK: 34_900,
        PRODUCT_MONITORING_MONTHLY: 49_900,
        PRODUCT_MONITORING_ANNUAL: 499_000,
    },
    "enterprise": {
        PRODUCT_ASSESSMENT: 119_000,
        PRODUCT_VALIDATION_CHECK: 59_000,
        PRODUCT_MONITORING_MONTHLY: 79_900,
        PRODUCT_MONITORING_ANNUAL: 799_000,
    },
    "enterprise_plus": {
        PRODUCT_ASSESSMENT: None,
        PRODUCT_VALIDATION_CHECK: None,
        PRODUCT_MONITORING_MONTHLY: None,
        PRODUCT_MONITORING_ANNUAL: None,
    },
}

LEGACY_FIXED_PRODUCT_KEYS = {
    PRODUCT_ASSESSMENT,
    PRODUCT_VALIDATION_CHECK,
    PRODUCT_MONITORING_MONTHLY,
    PRODUCT_MONITORING_ANNUAL,
}


def pricing_sku_key(tier_code: str, product_key: str) -> str:
    return f"{tier_code}__{product_key}"


def split_pricing_sku_key(value: str) -> tuple[str, str] | None:
    parts = str(value or "").split("__", 1)
    if len(parts) != 2:
        return None
    tier_code, product_key = parts
    if tier_code not in DEFAULT_TIER_PRICES_CENTS or product_key not in PRODUCT_DEFINITIONS:
        return None
    return tier_code, product_key


def tier_for_record_count(record_count: int) -> dict[str, Any]:
    normalized = max(int(record_count or 0), 0)
    for tier in VOLUME_TIERS:
        max_records = tier["max_records"]
        if normalized >= int(tier["min_records"]) and (max_records is None or normalized <= int(max_records)):
            return dict(tier)
    return dict(VOLUME_TIERS[-1])


def _build_product_pricing_defaults() -> dict[str, dict[str, Any]]:
    defaults: dict[str, dict[str, Any]] = {}
    for tier in VOLUME_TIERS:
        tier_code = str(tier["code"])
        if tier_code == "enterprise_plus":
            continue
        for product_key, product in PRODUCT_DEFINITIONS.items():
            price_cents = DEFAULT_TIER_PRICES_CENTS[tier_code][product_key]
            defaults[pricing_sku_key(tier_code, product_key)] = {
                "display_name": f"{product['display_name']} · {tier['display_name']}",
                "price_cents": int(price_cents or 0),
                "currency": "EUR",
                "billing_interval": str(product["billing_interval"]),
                "is_active": True,
                "tier_code": tier_code,
                "product_key": product_key,
            }
    return defaults


PRODUCT_PRICING_DEFAULTS: dict[str, dict[str, Any]] = _build_product_pricing_defaults()
PRODUCT_PRICING_ORDER = list(PRODUCT_PRICING_DEFAULTS.keys())


class ProductPricingValidationError(ValueError):
    pass


def ensure_default_product_pricing(db) -> None:
    now = utc_now()
    for sku_key in PRODUCT_PRICING_ORDER:
        config = PRODUCT_PRICING_DEFAULTS[sku_key]
        if db.get(ProductPricingConfig, sku_key) is not None:
            continue
        db.add(
            ProductPricingConfig(
                product_key=sku_key,
                display_name=str(config["display_name"]),
                price_cents=int(config["price_cents"]),
                currency=str(config["currency"]),
                billing_interval=str(config["billing_interval"]),
                is_active=bool(config["is_active"]),
                updated_at_utc=now,
            )
        )

    # Fixed B6 prices and pre-A4 rows remain historical compatibility data only.
    # They must not appear in active pricing projection after B6.1.
    for legacy_key in LEGACY_FIXED_PRODUCT_KEYS:
        row = db.get(ProductPricingConfig, legacy_key)
        if row is not None:
            row.is_active = False
            row.updated_at_utc = now
    db.commit()


def _sort_product_rows(rows: list[ProductPricingConfig]) -> list[ProductPricingConfig]:
    rank = {key: index for index, key in enumerate(PRODUCT_PRICING_ORDER)}
    return sorted(rows, key=lambda row: rank.get(row.product_key, 999))


def list_product_pricing(db, *, active_only: bool = False) -> list[ProductPricingConfig]:
    ensure_default_product_pricing(db)
    query = select(ProductPricingConfig).where(ProductPricingConfig.product_key.in_(PRODUCT_PRICING_ORDER))
    if active_only:
        query = query.where(ProductPricingConfig.is_active.is_(True))
    rows = list(db.scalars(query).all())
    return _sort_product_rows(rows)


def validate_product_pricing_update(
    *,
    product_key: str,
    display_name: str,
    price_cents: int,
    currency: str,
    billing_interval: str,
) -> None:
    if product_key not in PRODUCT_PRICING_DEFAULTS:
        raise ProductPricingValidationError("Unknown pricing tier/product key.")
    if not str(display_name or "").strip():
        raise ProductPricingValidationError("Display name is required.")
    if int(price_cents) <= 0:
        raise ProductPricingValidationError("Price must be greater than 0 cents.")
    if str(currency or "").strip().upper() != "EUR":
        raise ProductPricingValidationError("Only EUR pricing is supported.")
    expected_interval = PRODUCT_PRICING_DEFAULTS[product_key]["billing_interval"]
    if str(billing_interval or "").strip().lower() != expected_interval:
        raise ProductPricingValidationError(f"Billing interval for {product_key} must be {expected_interval}.")


def _pricing_row(db, *, tier_code: str, product_key: str) -> ProductPricingConfig:
    ensure_default_product_pricing(db)
    sku_key = pricing_sku_key(tier_code, product_key)
    if sku_key not in PRODUCT_PRICING_DEFAULTS:
        raise ProductPricingValidationError(f"Unsupported pricing SKU: {sku_key}")
    row = db.get(ProductPricingConfig, sku_key)
    if row is None:
        raise ProductPricingValidationError(f"Pricing SKU not configured: {sku_key}")
    return row


def get_tier_price(db, *, tier_code: str, product_key: str) -> ProductPricingConfig | None:
    if tier_code == "enterprise_plus":
        return None
    return _pricing_row(db, tier_code=tier_code, product_key=product_key)


def get_price_quote(db, *, record_count: int, product_key: str) -> dict[str, Any]:
    if product_key not in PRODUCT_DEFINITIONS:
        raise ProductPricingValidationError(f"Unsupported product: {product_key}")
    tier = tier_for_record_count(record_count)
    tier_code = str(tier["code"])
    if tier_code == "enterprise_plus":
        return {
            "pricing_model": PRICING_MODEL,
            "pricing_metric": PRICING_METRIC,
            "record_count": max(int(record_count or 0), 0),
            "tier_code": tier_code,
            "tier_name": tier["display_name"],
            "product_key": product_key,
            "custom_quote": True,
            "price_cents": None,
            "price_eur": None,
            "currency": "EUR",
            "billing_interval": PRODUCT_DEFINITIONS[product_key]["billing_interval"],
        }
    row = _pricing_row(db, tier_code=tier_code, product_key=product_key)
    price_cents = max(int(row.price_cents or 0), 0)
    return {
        "pricing_model": PRICING_MODEL,
        "pricing_metric": PRICING_METRIC,
        "record_count": max(int(record_count or 0), 0),
        "tier_code": tier_code,
        "tier_name": tier["display_name"],
        "tier_min_records": tier["min_records"],
        "tier_max_records": tier["max_records"],
        "product_key": product_key,
        "custom_quote": False,
        "price_cents": price_cents,
        "price_eur": round(price_cents / 100, 2),
        "currency": (row.currency or "EUR").upper(),
        "billing_interval": row.billing_interval,
        "is_active": bool(row.is_active),
        "updated_at": row.updated_at_utc.isoformat() if row.updated_at_utc else None,
    }


def product_price_to_public(row: ProductPricingConfig) -> dict[str, Any]:
    split = split_pricing_sku_key(row.product_key)
    tier_code, canonical_product_key = split if split else ("unknown", row.product_key)
    price_cents = max(int(row.price_cents or 0), 0)
    return {
        "sku_key": row.product_key,
        "tier_code": tier_code,
        "product_key": canonical_product_key,
        "display_name": row.display_name,
        "price_cents": price_cents,
        "price_eur": round(price_cents / 100, 2),
        "currency": (row.currency or "EUR").upper(),
        "billing_interval": row.billing_interval,
        "is_active": bool(row.is_active),
        "updated_at": row.updated_at_utc.isoformat() if row.updated_at_utc else None,
    }


def get_public_product_pricing_payload(db) -> dict[str, Any]:
    ensure_default_product_pricing(db)
    rows = list_product_pricing(db, active_only=True)
    by_key = {row.product_key: row for row in rows}
    tiers: list[dict[str, Any]] = []
    for tier in VOLUME_TIERS:
        tier_code = str(tier["code"])
        if tier_code == "enterprise_plus":
            tiers.append({**tier, "custom_quote": True, "prices": {}})
            continue
        prices: dict[str, Any] = {}
        for product_key in PRODUCT_DEFINITIONS:
            row = by_key[pricing_sku_key(tier_code, product_key)]
            prices[product_key] = product_price_to_public(row)
        tiers.append({**tier, "custom_quote": False, "prices": prices})

    small = tiers[0]["prices"]
    products = [
        {**small[PRODUCT_ASSESSMENT], "display_name": "Assessment", "is_from_price": True},
        {**small[PRODUCT_VALIDATION_CHECK], "display_name": "Validation Check", "is_from_price": True},
        {**small[PRODUCT_MONITORING_MONTHLY], "display_name": "Monitoring Monthly", "is_from_price": True},
        {**small[PRODUCT_MONITORING_ANNUAL], "display_name": "Monitoring Annual", "is_from_price": True},
    ]
    return {
        "source": "database",
        "currency": "EUR",
        "pricing_model": PRICING_MODEL,
        "pricing_metric": PRICING_METRIC,
        "price_dependency_copy": "Price depends on analyzed record volume.",
        "products": products,
        "tiers": tiers,
        "custom_quote_above_records": 20_000_000,
        "stripe_sync_warning": STRIPE_SYNC_WARNING,
    }


def get_product_price(db, product_key: str, *, record_count: int = 0) -> ProductPricingConfig:
    """Compatibility helper: resolve the configured row for the record-volume tier."""
    tier = tier_for_record_count(record_count)
    if tier["code"] == "enterprise_plus":
        raise ProductPricingValidationError("Enterprise+ requires a custom quote.")
    return _pricing_row(db, tier_code=str(tier["code"]), product_key=product_key)


def build_monitoring_pricing_breakdown(db, *, record_count: int = 0) -> dict[str, Any]:
    monthly = get_price_quote(db, record_count=record_count, product_key=PRODUCT_MONITORING_MONTHLY)
    annual = get_price_quote(db, record_count=record_count, product_key=PRODUCT_MONITORING_ANNUAL)
    if monthly["custom_quote"] or annual["custom_quote"]:
        return {
            "pricing_model": PRICING_MODEL,
            "pricing_metric": PRICING_METRIC,
            "record_count": max(int(record_count or 0), 0),
            "tier_code": "enterprise_plus",
            "custom_quote": True,
            "base_price_monthly": None,
            "final_price_monthly": None,
            "annual_fixed_price": None,
            "monthly_note": "Custom quote required for Enterprise+ record volume.",
            "annual_note": "Custom quote required for Enterprise+ record volume.",
        }
    return {
        "pricing_model": PRICING_MODEL,
        "pricing_metric": PRICING_METRIC,
        "record_count": max(int(record_count or 0), 0),
        "tier_code": monthly["tier_code"],
        "custom_quote": False,
        "base_price_monthly": monthly["price_eur"],
        "step_records": 0,
        "price_per_step": 0.0,
        "variable_price_monthly": 0.0,
        "raw_price_monthly": monthly["price_eur"],
        "final_price_monthly": monthly["price_eur"],
        "annual_fixed_price": annual["price_eur"],
        "monthly_note": f"Monitoring price for {monthly['tier_name']} ARV tier.",
        "annual_note": f"Annual Monitoring price for {annual['tier_name']} ARV tier.",
    }
