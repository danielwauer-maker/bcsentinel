from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from app.db import SessionLocal
from app.public_lead_models import PilotInterest
from app.routers.prepilot import router as prepilot_router
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


class PilotInterestRequest(BaseModel):
    contact_name: str = Field(min_length=2, max_length=120)
    contact_email: str = Field(min_length=5, max_length=255)
    company_name: str | None = Field(default=None, max_length=160)
    bc_context: str | None = Field(default=None, max_length=80)
    message: str | None = Field(default=None, max_length=3000)
    preferred_language: str = Field(default="de", max_length=10)
    source_page: str = Field(default="pilot", max_length=120)
    privacy_consent: bool
    website: str | None = Field(default=None, max_length=255)

    @field_validator("contact_email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("A valid email address is required.")
        return normalized


class PilotInterestResponse(BaseModel):
    status: str
    reference: str | None = None


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


@router.post("/public/pilot-interest", response_model=PilotInterestResponse, status_code=202)
def submit_pilot_interest(payload: PilotInterestRequest) -> PilotInterestResponse:
    if not payload.privacy_consent:
        raise HTTPException(status_code=400, detail="Privacy consent is required.")

    # Honeypot submissions are accepted without persistence so automated clients
    # do not learn whether spam protection was triggered.
    if (payload.website or "").strip():
        return PilotInterestResponse(status="accepted")

    language = (payload.preferred_language or "de").strip().lower()
    if language not in {"de", "en"}:
        language = "de"

    with SessionLocal() as db:
        row = PilotInterest(
            contact_name=payload.contact_name.strip(),
            contact_email=payload.contact_email,
            company_name=(payload.company_name or "").strip() or None,
            bc_context=(payload.bc_context or "").strip() or None,
            message=(payload.message or "").strip() or None,
            preferred_language=language,
            source_page=(payload.source_page or "pilot").strip() or "pilot",
            status="new",
            created_at_utc=datetime.now(timezone.utc),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return PilotInterestResponse(status="accepted", reference=f"PILOT-{row.id:06d}")


# Pre-pilot authentication/account APIs must be reachable before tenant selection.
# The aggregator keeps future X0 modules out of the public-page implementation.
router.include_router(prepilot_router)
