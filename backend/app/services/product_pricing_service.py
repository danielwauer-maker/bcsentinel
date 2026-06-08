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
PRODUCT_PRICING_ORDER = [
    PRODUCT_ASSESSMENT,
    PRODUCT_VALIDATION_CHECK,
    PRODUCT_MONITORING_MONTHLY,
    PRODUCT_MONITORING_ANNUAL,
]

PRODUCT_PRICING_DEFAULTS: dict[str, dict[str, Any]] = {
    PRODUCT_ASSESSMENT: {
        "display_name": "Assessment",
        "price_cents": 7900,
        "currency": "EUR",
        "billing_interval": PRODUCT_BILLING_INTERVAL_ONE_TIME,
        "is_active": True,
    },
    PRODUCT_VALIDATION_CHECK: {
        "display_name": "Validation Check",
        "price_cents": 4900,
        "currency": "EUR",
        "billing_interval": PRODUCT_BILLING_INTERVAL_ONE_TIME,
        "is_active": True,
    },
    PRODUCT_MONITORING_MONTHLY: {
        "display_name": "Monitoring Monthly",
        "price_cents": 9900,
        "currency": "EUR",
        "billing_interval": PRODUCT_BILLING_INTERVAL_MONTH,
        "is_active": True,
    },
    PRODUCT_MONITORING_ANNUAL: {
        "display_name": "Monitoring Annual",
        "price_cents": 99000,
        "currency": "EUR",
        "billing_interval": PRODUCT_BILLING_INTERVAL_YEAR,
        "is_active": True,
    },
}


class ProductPricingValidationError(ValueError):
    pass


def ensure_default_product_pricing(db) -> None:
    now = utc_now()
    for product_key in PRODUCT_PRICING_ORDER:
        config = PRODUCT_PRICING_DEFAULTS[product_key]
        if db.get(ProductPricingConfig, product_key) is not None:
            continue
        db.add(
            ProductPricingConfig(
                product_key=product_key,
                display_name=str(config["display_name"]),
                price_cents=int(config["price_cents"]),
                currency=str(config["currency"]),
                billing_interval=str(config["billing_interval"]),
                is_active=bool(config["is_active"]),
                updated_at_utc=now,
            )
        )
    db.commit()


def _sort_product_rows(rows: list[ProductPricingConfig]) -> list[ProductPricingConfig]:
    rank = {product_key: index for index, product_key in enumerate(PRODUCT_PRICING_ORDER)}
    return sorted(rows, key=lambda row: rank.get(row.product_key, 999))


def list_product_pricing(db, *, active_only: bool = False) -> list[ProductPricingConfig]:
    query = select(ProductPricingConfig)
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
        raise ProductPricingValidationError("Unknown product key.")
    if not str(display_name or "").strip():
        raise ProductPricingValidationError("Display name is required.")
    if int(price_cents) <= 0:
        raise ProductPricingValidationError("Price must be greater than 0 cents.")
    if str(currency or "").strip().upper() != "EUR":
        raise ProductPricingValidationError("Only EUR pricing is supported.")

    expected_interval = PRODUCT_PRICING_DEFAULTS[product_key]["billing_interval"]
    if str(billing_interval or "").strip().lower() != expected_interval:
        raise ProductPricingValidationError(f"Billing interval for {product_key} must be {expected_interval}.")


def product_price_to_public(row: ProductPricingConfig) -> dict[str, Any]:
    price_cents = max(int(row.price_cents or 0), 0)
    return {
        "product_key": row.product_key,
        "display_name": row.display_name,
        "price_cents": price_cents,
        "price_eur": round(price_cents / 100, 2),
        "currency": (row.currency or "EUR").upper(),
        "billing_interval": row.billing_interval,
        "is_active": bool(row.is_active),
        "updated_at": row.updated_at_utc.isoformat() if row.updated_at_utc else None,
    }


def get_product_price(db, product_key: str) -> ProductPricingConfig:
    ensure_default_product_pricing(db)
    row = db.get(ProductPricingConfig, product_key)
    if row is None:
        config = PRODUCT_PRICING_DEFAULTS[product_key]
        row = ProductPricingConfig(
            product_key=product_key,
            display_name=str(config["display_name"]),
            price_cents=int(config["price_cents"]),
            currency=str(config["currency"]),
            billing_interval=str(config["billing_interval"]),
            is_active=bool(config["is_active"]),
            updated_at_utc=utc_now(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def get_public_product_pricing_payload(db) -> dict[str, Any]:
    ensure_default_product_pricing(db)
    products = [product_price_to_public(row) for row in list_product_pricing(db, active_only=True)]
    return {
        "source": "database",
        "currency": "EUR",
        "products": products,
    }


def build_monitoring_pricing_breakdown(db) -> dict[str, Any]:
    monthly = get_product_price(db, PRODUCT_MONITORING_MONTHLY)
    annual = get_product_price(db, PRODUCT_MONITORING_ANNUAL)
    monthly_price = round(max(int(monthly.price_cents or 0), 0) / 100, 2)
    annual_price = round(max(int(annual.price_cents or 0), 0) / 100, 2)
    return {
        "base_price_monthly": monthly_price,
        "step_records": 0,
        "price_per_step": 0.0,
        "variable_price_monthly": 0.0,
        "raw_price_monthly": monthly_price,
        "final_price_monthly": monthly_price,
        "annual_fixed_price": annual_price,
        "monthly_note": "Monitoring Monthly list price from Product Pricing.",
        "annual_note": "Monitoring Annual list price from Product Pricing.",
    }
