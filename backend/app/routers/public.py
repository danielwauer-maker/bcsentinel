from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.db import SessionLocal
from app.services.impact_service import (
    EXPLICIT_ISSUE_IMPACTS,
    ensure_default_impact_config,
    get_hourly_rate_eur,
    get_impact_definition,
)
from app.services.product_pricing_service import build_public_pricing_matrix, get_public_product_pricing_payload
from app.services.landingpage_visibility_service import public_landingpage_visibility_payload

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
    starting_at: bool = False
    contact_sales: bool = False


class PublicProductPricingResponse(BaseModel):
    source: str
    currency: str
    products: list[PublicProductPricingItemResponse]
    matrix: list[dict[str, Any]] | None = None


class PublicLandingpageVisibilityItemResponse(BaseModel):
    page_key: str
    is_visible: bool


class PublicLandingpageVisibilityResponse(BaseModel):
    source: str
    pages: list[PublicLandingpageVisibilityItemResponse]


class PublicLossExampleIssueResponse(BaseModel):
    minutes_per_occurrence: float
    probability: float
    frequency_per_year: float


class PublicLossExampleConfigResponse(BaseModel):
    hourly_rate_eur: float
    issues: dict[str, PublicLossExampleIssueResponse]


@router.get("/pricing/public", response_model=PublicProductPricingResponse)
def get_public_product_pricing(include_matrix: bool = Query(default=False)) -> PublicProductPricingResponse:
    with SessionLocal() as db:
        payload = get_public_product_pricing_payload(db)
        if include_matrix:
            payload["matrix"] = build_public_pricing_matrix(db)
        return PublicProductPricingResponse.model_validate(payload)


@router.get("/landingpage/pages/visibility", response_model=PublicLandingpageVisibilityResponse)
def get_public_landingpage_visibility() -> PublicLandingpageVisibilityResponse:
    with SessionLocal() as db:
        return PublicLandingpageVisibilityResponse.model_validate(public_landingpage_visibility_payload(db))


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
