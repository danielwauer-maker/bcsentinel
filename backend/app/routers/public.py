from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.core.settings import settings
from app.db import SessionLocal
from app.models import PublicContactMessage
from app.security.rate_limit import require_rate_limit
from app.services.billing_service import utc_now
from app.services.dashboard_invite_service import _send_html_email
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
    product_contract: dict[str, Any]
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
    salutation: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    company: str | None = None
    email: str
    phone: str | None = None
    message: str
    intent: str | None = None
    language: str | None = None
    privacy_accepted: bool = False


class PublicContactResponse(BaseModel):
    status: str
    message_id: int
    delivery_status: str


def _normalize_public_contact_email(value: str) -> str:
    normalized = (value or "").strip().lower()
    if (
        not normalized
        or " " in normalized
        or "@" not in normalized
        or "." not in normalized.partition("@")[2]
    ):
        raise HTTPException(status_code=422, detail="A valid email address is required.")
    return normalized


def _clean(value: str | None, limit: int) -> str | None:
    normalized = (value or "").strip()
    return normalized[:limit] if normalized else None


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


@router.post("/public/contact", response_model=PublicContactResponse)
def submit_public_contact(payload: PublicContactRequest, request: Request) -> PublicContactResponse:
    require_rate_limit(
        request,
        action="public_contact",
        max_attempts=5,
        window_seconds=300,
    )
    if not payload.privacy_accepted:
        raise HTTPException(status_code=422, detail="Privacy acknowledgement is required.")

    email = _normalize_public_contact_email(payload.email)
    message = (payload.message or "").strip()
    if len(message) < 10:
        raise HTTPException(status_code=422, detail="Please enter a meaningful message.")
    message = message[:5000]

    with SessionLocal() as db:
        row = PublicContactMessage(
            salutation=_clean(payload.salutation, 30),
            first_name=_clean(payload.first_name, 100),
            last_name=_clean(payload.last_name, 100),
            company=_clean(payload.company, 160),
            email=email,
            phone=_clean(payload.phone, 60),
            message=message,
            intent=_clean(payload.intent, 80),
            language=_clean(payload.language, 10),
            privacy_accepted=True,
            mail_status="pending",
            created_at_utc=utc_now(),
        )
        db.add(row)
        db.flush()

        recipient = (settings.CONTACT_INBOX_EMAIL or settings.SMTP_FROM_EMAIL or "").strip()
        sent = False
        error: str | None = None
        if recipient:
            subject = f"[BCSentinel Contact] {row.intent or 'general'} · {row.company or row.email}"
            html_body = (
                "<h2>New BCSentinel contact request</h2>"
                f"<p><strong>From:</strong> {row.first_name or ''} {row.last_name or ''} &lt;{row.email}&gt;</p>"
                f"<p><strong>Company:</strong> {row.company or '-'}</p>"
                f"<p><strong>Phone:</strong> {row.phone or '-'}</p>"
                f"<p><strong>Intent:</strong> {row.intent or '-'}</p>"
                f"<p><strong>Message:</strong></p><p>{message.replace(chr(10), '<br>')}</p>"
            )
            sent, error = _send_html_email(
                target_email=recipient,
                subject=subject,
                html_body=html_body,
            )
        else:
            error = "Contact inbox email is not configured."

        row.mail_status = "sent" if sent else "stored"
        row.mail_error = None if sent else error
        db.commit()
        db.refresh(row)

        return PublicContactResponse(
            status="accepted",
            message_id=row.id,
            delivery_status=row.mail_status,
        )
