from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import ProductPricingConfig, ProductPricingMatrixConfig
from app.services.billing_service import utc_now
from app.services.product_license_service import (
    PRODUCT_DATA_HEALTH_SCORE,
    PRODUCT_FULL_ANALYSIS,
    PRODUCT_MONITORING_ANNUAL,
    PRODUCT_MONITORING_MONTHLY,
    PRODUCT_VALIDATION_CHECK,
    normalize_product_code,
    pricing_tier_for_record_count,
)

PRODUCT_BILLING_INTERVAL_ONE_TIME = "one_time"
PRODUCT_BILLING_INTERVAL_MONTH = "month"
PRODUCT_BILLING_INTERVAL_YEAR = "year"
PRODUCT_BILLING_INTERVAL_CONTACT_SALES = "contact_sales"
PRICING_TIER_STARTER = "starter"
PRICING_TIER_PROFESSIONAL = "professional"
PRICING_TIER_BUSINESS = "business"
PRICING_TIER_ENTERPRISE = "enterprise"
PRICING_TIER_ORDER = [
    PRICING_TIER_STARTER,
    PRICING_TIER_PROFESSIONAL,
    PRICING_TIER_BUSINESS,
    PRICING_TIER_ENTERPRISE,
]
PRICING_TIER_MAX_RECORDS = {
    PRICING_TIER_STARTER: 100_000,
    PRICING_TIER_PROFESSIONAL: 250_000,
    PRICING_TIER_BUSINESS: 500_000,
    PRICING_TIER_ENTERPRISE: None,
}
PRODUCT_PRICING_ORDER = [
    PRODUCT_DATA_HEALTH_SCORE,
    PRODUCT_FULL_ANALYSIS,
    PRODUCT_VALIDATION_CHECK,
    PRODUCT_MONITORING_MONTHLY,
    PRODUCT_MONITORING_ANNUAL,
]

PRODUCT_PRICING_DEFAULTS: dict[str, dict[str, Any]] = {
    PRODUCT_DATA_HEALTH_SCORE: {
        "display_name": "Data Health Score",
        "price_cents": 0,
        "currency": "EUR",
        "billing_interval": PRODUCT_BILLING_INTERVAL_ONE_TIME,
        "is_active": True,
    },
    PRODUCT_FULL_ANALYSIS: {
        "display_name": "Full Analysis",
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
        "price_cents": 14900,
        "currency": "EUR",
        "billing_interval": PRODUCT_BILLING_INTERVAL_MONTH,
        "is_active": True,
    },
    PRODUCT_MONITORING_ANNUAL: {
        "display_name": "Monitoring Annual",
        "price_cents": 149000,
        "currency": "EUR",
        "billing_interval": PRODUCT_BILLING_INTERVAL_YEAR,
        "is_active": True,
    },
}

PRODUCT_PRICING_MATRIX_DEFAULTS: dict[str, dict[str, dict[str, Any]]] = {
    PRODUCT_FULL_ANALYSIS: {
        PRICING_TIER_STARTER: {"amount_cents": 7900, "billing_interval": PRODUCT_BILLING_INTERVAL_ONE_TIME},
        PRICING_TIER_PROFESSIONAL: {"amount_cents": 9900, "billing_interval": PRODUCT_BILLING_INTERVAL_ONE_TIME},
        PRICING_TIER_BUSINESS: {"amount_cents": 12900, "billing_interval": PRODUCT_BILLING_INTERVAL_ONE_TIME},
        PRICING_TIER_ENTERPRISE: {"amount_cents": None, "billing_interval": PRODUCT_BILLING_INTERVAL_CONTACT_SALES},
    },
    PRODUCT_VALIDATION_CHECK: {
        PRICING_TIER_STARTER: {"amount_cents": 4900, "billing_interval": PRODUCT_BILLING_INTERVAL_ONE_TIME},
        PRICING_TIER_PROFESSIONAL: {"amount_cents": 7900, "billing_interval": PRODUCT_BILLING_INTERVAL_ONE_TIME},
        PRICING_TIER_BUSINESS: {"amount_cents": 9900, "billing_interval": PRODUCT_BILLING_INTERVAL_ONE_TIME},
        PRICING_TIER_ENTERPRISE: {"amount_cents": None, "billing_interval": PRODUCT_BILLING_INTERVAL_CONTACT_SALES},
    },
    PRODUCT_MONITORING_MONTHLY: {
        PRICING_TIER_STARTER: {"amount_cents": 14900, "billing_interval": PRODUCT_BILLING_INTERVAL_MONTH},
        PRICING_TIER_PROFESSIONAL: {"amount_cents": 19900, "billing_interval": PRODUCT_BILLING_INTERVAL_MONTH},
        PRICING_TIER_BUSINESS: {"amount_cents": 29900, "billing_interval": PRODUCT_BILLING_INTERVAL_MONTH},
        PRICING_TIER_ENTERPRISE: {"amount_cents": None, "billing_interval": PRODUCT_BILLING_INTERVAL_CONTACT_SALES},
    },
    PRODUCT_MONITORING_ANNUAL: {
        PRICING_TIER_STARTER: {"amount_cents": 149000, "billing_interval": PRODUCT_BILLING_INTERVAL_YEAR},
        PRICING_TIER_PROFESSIONAL: {"amount_cents": 199000, "billing_interval": PRODUCT_BILLING_INTERVAL_YEAR},
        PRICING_TIER_BUSINESS: {"amount_cents": 299000, "billing_interval": PRODUCT_BILLING_INTERVAL_YEAR},
        PRICING_TIER_ENTERPRISE: {"amount_cents": None, "billing_interval": PRODUCT_BILLING_INTERVAL_CONTACT_SALES},
    },
}

PRODUCT_PRICING_MATRIX_PRODUCTS = list(PRODUCT_PRICING_MATRIX_DEFAULTS.keys())
PRODUCT_MATRIX_DISPLAY_NAMES = {
    PRODUCT_FULL_ANALYSIS: {"de": "Full Analysis", "en": "Full Analysis"},
    PRODUCT_VALIDATION_CHECK: {"de": "Validation Check", "en": "Validation Check"},
    PRODUCT_MONITORING_MONTHLY: {"de": "Monitoring Monthly", "en": "Monitoring Monthly"},
    PRODUCT_MONITORING_ANNUAL: {"de": "Monitoring Annual", "en": "Monitoring Annual"},
}


@dataclass(frozen=True)
class MatrixPrice:
    product_key: str
    pricing_tier: str
    max_records: int | None
    amount_cents: int | None
    currency: str
    billing_interval: str
    display_name_de: str
    display_name_en: str
    stripe_price_id: str | None
    is_active: bool

    @property
    def amount_eur(self) -> float | None:
        if self.amount_cents is None:
            return None
        return round(max(int(self.amount_cents or 0), 0) / 100, 2)

    @property
    def contact_sales(self) -> bool:
        return self.billing_interval == PRODUCT_BILLING_INTERVAL_CONTACT_SALES or self.amount_cents is None


class ProductPricingValidationError(ValueError):
    pass


def calculate_pricing_tier(record_count: int | None) -> str | None:
    return pricing_tier_for_record_count(record_count)


def ensure_default_product_pricing(db) -> None:
    now = utc_now()
    for product_key in PRODUCT_PRICING_ORDER:
        config = PRODUCT_PRICING_DEFAULTS[product_key]
        if db.get(ProductPricingConfig, product_key) is not None:
            continue
        try:
            with db.begin_nested():
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
                db.flush()
        except IntegrityError:
            # Another instance initialized the same immutable default first.
            # The savepoint keeps the caller transaction usable.
            pass
    db.commit()


def ensure_default_product_pricing_matrix(db) -> None:
    now = utc_now()
    for product_key in PRODUCT_PRICING_MATRIX_PRODUCTS:
        for pricing_tier in PRICING_TIER_ORDER:
            if db.scalar(
                select(ProductPricingMatrixConfig).where(
                    ProductPricingMatrixConfig.product_key == product_key,
                    ProductPricingMatrixConfig.pricing_tier == pricing_tier,
                )
            ) is not None:
                continue
            config = PRODUCT_PRICING_MATRIX_DEFAULTS[product_key][pricing_tier]
            names = PRODUCT_MATRIX_DISPLAY_NAMES[product_key]
            try:
                with db.begin_nested():
                    db.add(
                        ProductPricingMatrixConfig(
                            product_key=product_key,
                            pricing_tier=pricing_tier,
                            max_records=PRICING_TIER_MAX_RECORDS[pricing_tier],
                            amount_cents=config["amount_cents"],
                            currency="EUR",
                            billing_interval=config["billing_interval"],
                            display_name_de=names["de"],
                            display_name_en=names["en"],
                            stripe_price_id=None,
                            is_active=True,
                            updated_at_utc=now,
                        )
                    )
                    db.flush()
            except IntegrityError:
                pass
    db.commit()


def _sort_product_rows(rows: list[ProductPricingConfig]) -> list[ProductPricingConfig]:
    rank = {product_key: index for index, product_key in enumerate(PRODUCT_PRICING_ORDER)}
    return sorted(rows, key=lambda row: rank.get(row.product_key, 999))


def list_product_pricing(db, *, active_only: bool = False) -> list[ProductPricingConfig]:
    query = select(ProductPricingConfig)
    if active_only:
        query = query.where(ProductPricingConfig.is_active.is_(True))
    rows = list(db.scalars(query).all())
    rows = [
        row
        for row in rows
        if not (
            normalize_product_code(row.product_key) in PRODUCT_PRICING_DEFAULTS
            and row.product_key != normalize_product_code(row.product_key)
        )
    ]
    return _sort_product_rows(rows)


def validate_product_pricing_update(
    *,
    product_key: str,
    display_name: str,
    price_cents: int,
    currency: str,
    billing_interval: str,
) -> None:
    normalized_product_key = normalize_product_code(product_key)
    if normalized_product_key not in PRODUCT_PRICING_DEFAULTS:
        raise ProductPricingValidationError("Unknown product key.")
    if not str(display_name or "").strip():
        raise ProductPricingValidationError("Display name is required.")
    if normalized_product_key == PRODUCT_DATA_HEALTH_SCORE:
        if int(price_cents) != 0:
            raise ProductPricingValidationError("Data Health Score must remain free.")
    elif int(price_cents) <= 0:
        raise ProductPricingValidationError("Price must be greater than 0 cents.")
    if str(currency or "").strip().upper() != "EUR":
        raise ProductPricingValidationError("Only EUR pricing is supported.")

    expected_interval = PRODUCT_PRICING_DEFAULTS[normalized_product_key]["billing_interval"]
    if str(billing_interval or "").strip().lower() != expected_interval:
        raise ProductPricingValidationError(f"Billing interval for {normalized_product_key} must be {expected_interval}.")


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
    normalized_product_key = normalize_product_code(product_key)
    row = db.get(ProductPricingConfig, normalized_product_key)
    if row is None:
        config = PRODUCT_PRICING_DEFAULTS[normalized_product_key]
        row = ProductPricingConfig(
            product_key=normalized_product_key,
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
    ensure_default_product_pricing_matrix(db)
    products = build_public_pricing_summary(db)
    return {
        "source": "database",
        "currency": "EUR",
        "products": products,
    }


def _matrix_rank(row: ProductPricingMatrixConfig) -> tuple[int, int]:
    product_rank = {product_key: index for index, product_key in enumerate(PRODUCT_PRICING_MATRIX_PRODUCTS)}
    tier_rank = {tier: index for index, tier in enumerate(PRICING_TIER_ORDER)}
    return (product_rank.get(row.product_key, 999), tier_rank.get(row.pricing_tier, 999))


def list_product_pricing_matrix(db, *, active_only: bool = False) -> list[ProductPricingMatrixConfig]:
    ensure_default_product_pricing_matrix(db)
    query = select(ProductPricingMatrixConfig)
    if active_only:
        query = query.where(ProductPricingMatrixConfig.is_active.is_(True))
    rows = list(db.scalars(query).all())
    return sorted(rows, key=_matrix_rank)


def _matrix_row_to_price(row: ProductPricingMatrixConfig) -> MatrixPrice:
    return MatrixPrice(
        product_key=normalize_product_code(row.product_key),
        pricing_tier=(row.pricing_tier or "").strip().lower(),
        max_records=row.max_records,
        amount_cents=row.amount_cents,
        currency=(row.currency or "EUR").upper(),
        billing_interval=(row.billing_interval or PRODUCT_BILLING_INTERVAL_ONE_TIME).strip().lower(),
        display_name_de=row.display_name_de or PRODUCT_MATRIX_DISPLAY_NAMES.get(row.product_key, {}).get("de", row.product_key),
        display_name_en=row.display_name_en or PRODUCT_MATRIX_DISPLAY_NAMES.get(row.product_key, {}).get("en", row.product_key),
        stripe_price_id=(row.stripe_price_id or "").strip() or None,
        is_active=bool(row.is_active),
    )


def get_matrix_price(db, product_key: str, pricing_tier: str) -> MatrixPrice:
    ensure_default_product_pricing_matrix(db)
    normalized_product = normalize_product_code(product_key)
    normalized_tier = (pricing_tier or PRICING_TIER_STARTER).strip().lower()
    if normalized_tier not in PRICING_TIER_ORDER:
        normalized_tier = PRICING_TIER_STARTER
    row = db.scalar(
        select(ProductPricingMatrixConfig).where(
            ProductPricingMatrixConfig.product_key == normalized_product,
            ProductPricingMatrixConfig.pricing_tier == normalized_tier,
        )
    )
    if row is None:
        defaults = PRODUCT_PRICING_MATRIX_DEFAULTS[normalized_product][normalized_tier]
        names = PRODUCT_MATRIX_DISPLAY_NAMES[normalized_product]
        return MatrixPrice(
            product_key=normalized_product,
            pricing_tier=normalized_tier,
            max_records=PRICING_TIER_MAX_RECORDS[normalized_tier],
            amount_cents=defaults["amount_cents"],
            currency="EUR",
            billing_interval=defaults["billing_interval"],
            display_name_de=names["de"],
            display_name_en=names["en"],
            stripe_price_id=None,
            is_active=True,
        )
    return _matrix_row_to_price(row)


def price_to_dashboard_item(price: MatrixPrice) -> dict[str, Any]:
    payload = {
        "product_key": price.product_key,
        "pricing_tier": price.pricing_tier,
        "label": price.display_name_en,
        "display_name_de": price.display_name_de,
        "display_name_en": price.display_name_en,
        "amount_eur": price.amount_eur,
        "currency": price.currency,
        "billing_interval": price.billing_interval,
        "contact_sales": price.contact_sales,
        "active": price.is_active,
    }
    if price.product_key in {PRODUCT_FULL_ANALYSIS, PRODUCT_VALIDATION_CHECK}:
        payload["access_days"] = 7
    if price.product_key == PRODUCT_MONITORING_MONTHLY:
        payload["interval"] = "month"
    if price.product_key == PRODUCT_MONITORING_ANNUAL:
        payload["interval"] = "year"
    return payload


def build_tier_pricing_payload(db, *, record_count: int | None) -> dict[str, Any]:
    pricing_tier = pricing_tier_for_record_count(record_count) or PRICING_TIER_STARTER
    prices = {
        product_key: price_to_dashboard_item(get_matrix_price(db, product_key, pricing_tier))
        for product_key in PRODUCT_PRICING_MATRIX_PRODUCTS
    }
    return {
        "record_count": record_count,
        "pricing_tier": pricing_tier,
        "contact_sales": pricing_tier == PRICING_TIER_ENTERPRISE,
        "prices": prices,
    }


def build_public_pricing_summary(db) -> list[dict[str, Any]]:
    rows = list_product_pricing_matrix(db, active_only=True)
    by_product: dict[str, list[MatrixPrice]] = {}
    for row in rows:
        price = _matrix_row_to_price(row)
        by_product.setdefault(price.product_key, []).append(price)

    def starting_price(product_key: str) -> MatrixPrice | None:
        candidates = [
            price
            for price in by_product.get(product_key, [])
            if not price.contact_sales and price.amount_cents is not None
        ]
        if candidates:
            return sorted(candidates, key=lambda price: int(price.amount_cents or 0))[0]
        return None

    full_analysis = starting_price(PRODUCT_FULL_ANALYSIS)
    validation = starting_price(PRODUCT_VALIDATION_CHECK)
    monitoring = starting_price(PRODUCT_MONITORING_MONTHLY)
    products = [
        {
            "product_key": PRODUCT_DATA_HEALTH_SCORE,
            "display_name": "Data Health Score",
            "price_cents": 0,
            "price_eur": 0.0,
            "currency": "EUR",
            "billing_interval": PRODUCT_BILLING_INTERVAL_ONE_TIME,
            "is_active": True,
            "starting_at": False,
            "contact_sales": False,
        },
    ]
    if full_analysis is not None:
        products.append(
            {
                "product_key": PRODUCT_FULL_ANALYSIS,
                "display_name": full_analysis.display_name_en,
                "price_cents": int(full_analysis.amount_cents or 0),
                "price_eur": full_analysis.amount_eur or 0.0,
                "currency": full_analysis.currency,
                "billing_interval": full_analysis.billing_interval,
                "is_active": full_analysis.is_active,
                "starting_at": True,
                "contact_sales": False,
            }
        )
    if validation is not None:
        products.append(
            {
                "product_key": PRODUCT_VALIDATION_CHECK,
                "display_name": validation.display_name_en,
                "price_cents": int(validation.amount_cents or 0),
                "price_eur": validation.amount_eur or 0.0,
                "currency": validation.currency,
                "billing_interval": validation.billing_interval,
                "is_active": validation.is_active,
                "starting_at": True,
                "contact_sales": False,
            }
        )
    if monitoring is not None:
        products.append(
            {
                "product_key": "monitoring",
                "display_name": "Monitoring",
                "price_cents": int(monitoring.amount_cents or 0),
                "price_eur": monitoring.amount_eur or 0.0,
                "currency": monitoring.currency,
                "billing_interval": PRODUCT_BILLING_INTERVAL_MONTH,
                "is_active": monitoring.is_active,
                "starting_at": True,
                "contact_sales": False,
            }
        )
    return products


def build_public_pricing_matrix(db) -> list[dict[str, Any]]:
    return [
        price_to_dashboard_item(_matrix_row_to_price(row))
        | {
            "max_records": row.max_records,
            "amount_cents": row.amount_cents,
            "stripe_price_configured": bool((row.stripe_price_id or "").strip()),
        }
        for row in list_product_pricing_matrix(db, active_only=True)
    ]


def resolve_checkout_matrix_price(
    db,
    *,
    product_key: str,
    record_count: int | None,
    env_price_id: str | None = None,
) -> MatrixPrice:
    pricing_tier = pricing_tier_for_record_count(record_count) or PRICING_TIER_STARTER
    price = get_matrix_price(db, product_key, pricing_tier)
    if not price.stripe_price_id and env_price_id and not price.contact_sales:
        return MatrixPrice(
            product_key=price.product_key,
            pricing_tier=price.pricing_tier,
            max_records=price.max_records,
            amount_cents=price.amount_cents,
            currency=price.currency,
            billing_interval=price.billing_interval,
            display_name_de=price.display_name_de,
            display_name_en=price.display_name_en,
            stripe_price_id=env_price_id.strip(),
            is_active=price.is_active,
        )
    return price


def build_monitoring_pricing_breakdown(db) -> dict[str, Any]:
    monthly = get_matrix_price(db, PRODUCT_MONITORING_MONTHLY, PRICING_TIER_STARTER)
    annual = get_matrix_price(db, PRODUCT_MONITORING_ANNUAL, PRICING_TIER_STARTER)
    monthly_price = monthly.amount_eur or 0.0
    annual_price = annual.amount_eur or 0.0
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
