from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.db import SessionLocal
from app.services.impact_service import (
    EXPLICIT_ISSUE_IMPACTS,
    ensure_default_impact_config,
    get_hourly_rate_eur,
    get_impact_definition,
)
from app.services.product_pricing_service import (
    PRODUCT_DEFINITIONS,
    ProductPricingValidationError,
    get_price_quote,
    get_public_product_pricing_payload,
)

router = APIRouter(tags=["public"])


class PublicProductPricingItemResponse(BaseModel):
    sku_key: str | None = None
    tier_code: str | None = None
    product_key: str
    display_name: str
    price_cents: int
    price_eur: float
    currency: str
    billing_interval: str
    is_active: bool
    is_from_price: bool = False
    updated_at: str | None = None


class PublicPricingTierResponse(BaseModel):
    code: str
    display_name: str
    min_records: int
    max_records: int | None = None
    custom_quote: bool
    prices: dict = Field(default_factory=dict)


class PublicProductPricingResponse(BaseModel):
    source: str
    currency: str
    pricing_model: str
    pricing_metric: str
    price_dependency_copy: str
    products: list[PublicProductPricingItemResponse]
    tiers: list[PublicPricingTierResponse]
    custom_quote_above_records: int
    stripe_sync_warning: str


class PublicPricingQuoteResponse(BaseModel):
    pricing_model: str
    pricing_metric: str
    record_count: int
    tier_code: str
    tier_name: str
    product_key: str
    custom_quote: bool
    price_cents: int | None = None
    price_eur: float | None = None
    currency: str
    billing_interval: str
    tier_min_records: int | None = None
    tier_max_records: int | None = None
    is_active: bool | None = None
    updated_at: str | None = None


class PublicLossExampleIssueResponse(BaseModel):
    minutes_per_occurrence: float
    probability: float
    frequency_per_year: float


class PublicLossExampleConfigResponse(BaseModel):
    hourly_rate_eur: float
    issues: dict[str, PublicLossExampleIssueResponse]


@router.get("/pricing/public", response_model=PublicProductPricingResponse)
def get_public_product_pricing() -> PublicProductPricingResponse:
    with SessionLocal() as db:
        return PublicProductPricingResponse.model_validate(get_public_product_pricing_payload(db))


@router.get("/pricing/quote", response_model=PublicPricingQuoteResponse)
def get_public_pricing_quote(
    product_key: str = Query(...),
    record_count: int = Query(..., ge=0),
) -> PublicPricingQuoteResponse:
    normalized_product_key = (product_key or "").strip().lower()
    if normalized_product_key not in PRODUCT_DEFINITIONS:
        raise HTTPException(status_code=400, detail="Unsupported product_key.")
    try:
        with SessionLocal() as db:
            quote = get_price_quote(db, record_count=record_count, product_key=normalized_product_key)
    except ProductPricingValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return PublicPricingQuoteResponse.model_validate(quote)


@router.get("/public/loss-examples-config", response_model=PublicLossExampleConfigResponse)
def get_public_loss_examples_config() -> PublicLossExampleConfigResponse:
    with SessionLocal() as db:
        ensure_default_impact_config(db)
        issues = {
            code: PublicLossExampleIssueResponse(
                minutes_per_occurrence=definition.minutes_per_occurrence,
                probability=definition.probability,
                frequency_per_year=definition.frequency_per_year,
            )
            for code in sorted(EXPLICIT_ISSUE_IMPACTS.keys())
            for definition in [get_impact_definition(db, code)]
        }
        return PublicLossExampleConfigResponse(
            hourly_rate_eur=round(get_hourly_rate_eur(db), 2),
            issues=issues,
        )
