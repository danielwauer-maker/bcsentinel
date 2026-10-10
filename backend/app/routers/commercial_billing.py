from __future__ import annotations

from datetime import datetime

import stripe
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.core.settings import settings
from app.db import SessionLocal
from app.models import PartnerReferral, Tenant
from app.routers.billing import (
    _billing_interval_for_product,
    _load_latest_pricing_scan,
    _normalize_checkout_product_code,
    _require_stripe_secret_key,
    _resolve_checkout_cancel_url,
    _resolve_checkout_success_url,
    _resolve_product_price_id,
    _scan_record_count,
    _verify_stripe_price_matches_quote,
    CheckoutSessionRequest,
)
from app.security.tenant import enforce_tenant_match, load_authenticated_tenant, require_tenant_headers
from app.services.commercial_checkout_service import checkout_discount_configuration
from app.services.entitlement_guard_service import require_tenant_feature
from app.services.product_license_service import is_one_time_product
from app.services.product_pricing_service import get_price_quote

router = APIRouter(tags=["commercial-billing"])


class CommercialCheckoutResponse(BaseModel):
    tenant_id: str
    product_code: str
    billing_interval: str
    pricing_tier: str
    list_price_cents: int
    effective_price_cents: int
    price_source: str
    promotion_code_allowed: bool
    sponsored: bool = False
    sponsorship_valid_until_utc: datetime | None = None
    checkout_required: bool
    checkout_session_id: str | None = None
    checkout_url: str | None = None
    provider: str | None = None


@router.post("/billing/checkout/commercial-session", response_model=CommercialCheckoutResponse)
def create_commercial_checkout_session(
    payload: CheckoutSessionRequest,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> CommercialCheckoutResponse:
    header_tenant_id, credential = tenant_auth
    enforce_tenant_match(payload.tenant_id, header_tenant_id, "Payload tenant_id")
    product_code = _normalize_checkout_product_code(payload)

    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, header_tenant_id, credential)
        require_tenant_feature(db, tenant, "billing_checkout")
        latest_scan = _load_latest_pricing_scan(db, tenant.tenant_id)
        if latest_scan is None:
            raise HTTPException(
                status_code=409,
                detail="A governed BCSentinel scan is required before self-service checkout can determine the ARV pricing tier.",
            )
        record_count = _scan_record_count(latest_scan)
        quote = get_price_quote(db, record_count=record_count, product_key=product_code)
        referral = db.scalar(select(PartnerReferral).where(PartnerReferral.tenant_id == tenant.tenant_id))

        if quote.get("custom_quote"):
            raise HTTPException(status_code=409, detail="Enterprise+ volume requires an individual quote.")

        commercial = checkout_discount_configuration(
            db,
            tenant_id=tenant.tenant_id,
            product_code=product_code,
            list_price_cents=int(quote["price_cents"]),
        )
        sponsorship_valid_until = commercial.get("pilot_sponsorship_valid_until_utc")
        if not commercial["checkout_required"]:
            return CommercialCheckoutResponse(
                tenant_id=tenant.tenant_id,
                product_code=product_code,
                billing_interval=_billing_interval_for_product(product_code, payload.billing_interval),
                pricing_tier=str(quote["tier_code"]),
                list_price_cents=int(commercial["list_price_cents"]),
                effective_price_cents=0,
                price_source="pilot_sponsorship",
                promotion_code_allowed=False,
                sponsored=True,
                sponsorship_valid_until_utc=sponsorship_valid_until,
                checkout_required=False,
            )

        coupon_id = commercial.get("coupon_id")
        override_id = commercial.get("override_id")
        effective_price_cents = int(commercial["effective_price_cents"])
        allow_promotion_codes = bool(commercial["allow_promotion_codes"])

    stripe.api_key = _require_stripe_secret_key()
    price_id = _resolve_product_price_id(product_code, str(quote["tier_code"]))
    _verify_stripe_price_matches_quote(price_id, quote, product_code)

    billing_interval = _billing_interval_for_product(product_code, payload.billing_interval)
    metadata = {
        "tenant_id": payload.tenant_id,
        "plan_code": product_code,
        "product_code": product_code,
        "billing_interval": billing_interval,
        "pricing_tier": str(quote["tier_code"]),
        "pricing_model": "record_volume_tiers",
        "bcsentinel_list_price_cents": str(quote["price_cents"]),
        "bcsentinel_effective_price_cents": str(effective_price_cents),
        "bcsentinel_price_source": str(commercial["price_source"]),
    }
    if override_id is not None:
        metadata["bcsentinel_override_id"] = str(override_id)
    if coupon_id:
        metadata["bcsentinel_coupon_id"] = str(coupon_id)
    if referral is not None:
        metadata["referral_code"] = str(referral.referral_code or "").strip().lower()
        metadata["attribution_source"] = str(referral.attribution_source or "").strip().lower()

    try:
        success_url = _resolve_checkout_success_url()
        cancel_url = _resolve_checkout_cancel_url()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    checkout_mode = "payment" if is_one_time_product(product_code) else "subscription"
    session_kwargs: dict = {
        "mode": checkout_mode,
        "client_reference_id": payload.tenant_id,
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": success_url,
        "cancel_url": cancel_url,
        "metadata": metadata,
        "billing_address_collection": "required",
    }
    if coupon_id:
        session_kwargs["discounts"] = [{"coupon": coupon_id}]
    elif allow_promotion_codes:
        session_kwargs["allow_promotion_codes"] = True
    if checkout_mode == "subscription":
        session_kwargs["subscription_data"] = {"metadata": metadata}

    try:
        session = stripe.checkout.Session.create(**session_kwargs)
    except stripe.error.InvalidRequestError as exc:
        raise HTTPException(status_code=400, detail="Stripe rejected the commercial checkout request.") from exc

    return CommercialCheckoutResponse(
        tenant_id=payload.tenant_id,
        product_code=product_code,
        billing_interval=billing_interval,
        pricing_tier=str(quote["tier_code"]),
        list_price_cents=int(commercial["list_price_cents"]),
        effective_price_cents=effective_price_cents,
        price_source=str(commercial["price_source"]),
        promotion_code_allowed=allow_promotion_codes,
        checkout_required=True,
        checkout_session_id=str(getattr(session, "id", "") or ""),
        checkout_url=str(getattr(session, "url", "") or ""),
        provider="stripe",
    )
