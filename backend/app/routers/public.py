from __future__ import annotations

import re
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field, field_validator

from app.core.settings import settings
from app.db import SessionLocal
from app.security.rate_limit import require_rate_limit
from app.services.impact_service import (
    EXPLICIT_ISSUE_IMPACTS,
    ensure_default_impact_config,
    get_hourly_rate_eur,
    get_impact_definition,
)
from app.services.product_pricing_service import build_public_pricing_matrix, get_public_product_pricing_payload
from app.services.landingpage_visibility_service import public_landingpage_visibility_payload
from app.services.public_contact_service import (
    ContactDeliveryFailed,
    ContactDeliveryUnavailable,
    PublicContactMessage,
    send_public_contact_message,
)

router = APIRouter(tags=["public"])
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
ALLOWED_TOPICS = {"Pricing", "Partner", "Support", "Pilot", "General"}


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


class PublicContactRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=254)
    company: str | None = Field(default=None, max_length=160)
    topic: str = Field(default="General", max_length=40)
    message: str = Field(min_length=10, max_length=5000)
    locale: Literal["de", "en"] = "de"
    website: str | None = Field(default=None, max_length=200)

    @field_validator("name", "email", "company", "topic", "message", "website", mode="before")
    @classmethod
    def strip_strings(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.lower()
        if not EMAIL_PATTERN.fullmatch(normalized):
            raise ValueError("invalid email address")
        return normalized

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, value: str) -> str:
        return value if value in ALLOWED_TOPICS else "General"


class PublicContactResponse(BaseModel):
    accepted: bool
    request_id: str | None = None


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


@router.post("/public/contact", response_model=PublicContactResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_public_contact(payload: PublicContactRequest, request: Request) -> PublicContactResponse:
    request_id = getattr(request.state, "request_id", None)

    # Honeypot submissions receive the same accepted response without delivery.
    if payload.website:
        return PublicContactResponse(accepted=True, request_id=request_id)

    require_rate_limit(
        request,
        action="public_contact",
        max_attempts=settings.CONTACT_RATE_LIMIT_ATTEMPTS,
        window_seconds=settings.CONTACT_RATE_LIMIT_WINDOW_SECONDS,
    )

    try:
        send_public_contact_message(
            PublicContactMessage(
                name=payload.name,
                email=payload.email,
                company=payload.company or None,
                topic=payload.topic,
                message=payload.message,
                locale=payload.locale,
                request_id=request_id,
            )
        )
    except ContactDeliveryUnavailable as exc:
        raise HTTPException(status_code=503, detail="Contact delivery is temporarily unavailable.") from exc
    except ContactDeliveryFailed as exc:
        raise HTTPException(status_code=502, detail="Contact delivery failed. Please retry later.") from exc

    return PublicContactResponse(accepted=True, request_id=request_id)
