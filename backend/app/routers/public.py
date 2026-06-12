from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.db import SessionLocal
from app.services.impact_service import (
    EXPLICIT_ISSUE_IMPACTS,
    ensure_default_impact_config,
    get_hourly_rate_eur,
    get_impact_definition,
)
from app.services.product_pricing_service import get_public_product_pricing_payload

router = APIRouter(tags=["public"])


class PublicProductPricingItemResponse(BaseModel):
    product_key: str
    display_name: str
    price_cents: int
    price_eur: float
    currency: str
    billing_interval: str
    is_active: bool
    updated_at: str | None = None


class PublicProductPricingResponse(BaseModel):
    source: str
    currency: str
    products: list[PublicProductPricingItemResponse]


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
