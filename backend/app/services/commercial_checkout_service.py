from __future__ import annotations

import math
from datetime import datetime, timezone

import stripe
from sqlalchemy import or_, select

from app.commercial_override_models import TenantCommercialOverride, TenantPilotSponsorship
from app.services.product_license_service import is_one_time_product, normalize_product_code
from app.services.tenant_commercial_service import calculate_effective_price, get_active_commercial_override


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def get_active_pilot_sponsorship(db, *, tenant_id: str, product_code: str, at_utc: datetime | None = None) -> TenantPilotSponsorship | None:
    moment = _as_utc(at_utc) or utc_now()
    rows = db.scalars(
        select(TenantPilotSponsorship).where(
            TenantPilotSponsorship.tenant_id == tenant_id,
            TenantPilotSponsorship.product_code == normalize_product_code(product_code),
            TenantPilotSponsorship.status == "active",
            TenantPilotSponsorship.valid_from_utc <= moment,
            TenantPilotSponsorship.valid_until_utc > moment,
        )
    ).all()
    if len(rows) > 1:
        raise RuntimeError("Multiple active pilot sponsorships found for tenant/product.")
    return rows[0] if rows else None


def commercial_quote(db, *, tenant_id: str, product_code: str, list_price_cents: int, currency: str = "EUR") -> dict:
    sponsorship = get_active_pilot_sponsorship(db, tenant_id=tenant_id, product_code=product_code)
    quote = calculate_effective_price(
        db,
        tenant_id=tenant_id,
        product_code=product_code,
        list_price_cents=list_price_cents,
        currency=currency,
    )
    quote["pilot_sponsorship_active"] = sponsorship is not None
    quote["pilot_sponsorship_id"] = sponsorship.id if sponsorship is not None else None
    quote["pilot_sponsorship_valid_until_utc"] = sponsorship.valid_until_utc if sponsorship is not None else None
    return quote


def _recurring_coupon_duration(override: TenantCommercialOverride) -> dict:
    end = _as_utc(override.valid_until_utc)
    if end is None:
        return {"duration": "forever"}
    remaining_days = max((end - utc_now()).total_seconds() / 86400.0, 1.0)
    months = max(1, min(int(math.ceil(remaining_days / 30.4375)), 36))
    return {"duration": "repeating", "duration_in_months": months}


def create_stripe_override_coupon(*, override: TenantCommercialOverride, list_price_cents: int, effective_price_cents: int,
                                  product_code: str) -> str | None:
    discount_cents = max(int(list_price_cents) - int(effective_price_cents), 0)
    if discount_cents <= 0:
        return None
    coupon_kwargs: dict = {
        "amount_off": discount_cents,
        "currency": "eur",
        "max_redemptions": 1,
        "name": f"BCSentinel tenant offer #{override.id}"[:40],
        "metadata": {
            "bcsentinel_override_id": str(override.id),
            "tenant_id": override.tenant_id,
            "product_code": product_code,
            "list_price_cents": str(list_price_cents),
            "effective_price_cents": str(effective_price_cents),
        },
    }
    if is_one_time_product(product_code):
        coupon_kwargs["duration"] = "once"
    else:
        coupon_kwargs.update(_recurring_coupon_duration(override))
    coupon = stripe.Coupon.create(**coupon_kwargs)
    return str(getattr(coupon, "id", "") or "").strip() or None


def checkout_discount_configuration(db, *, tenant_id: str, product_code: str, list_price_cents: int) -> dict:
    quote = commercial_quote(
        db,
        tenant_id=tenant_id,
        product_code=product_code,
        list_price_cents=list_price_cents,
        currency="EUR",
    )
    if quote["pilot_sponsorship_active"]:
        return {**quote, "checkout_required": False, "allow_promotion_codes": False, "coupon_id": None}

    override = get_active_commercial_override(db, tenant_id=tenant_id, product_code=product_code)
    if override is None:
        return {**quote, "checkout_required": True, "allow_promotion_codes": True, "coupon_id": None}

    if override.allow_promotion_code_stack:
        # Stripe Checkout supports one explicit discount object. BCSentinel deliberately
        # does not combine a tenant override and a customer-entered promotion code until
        # a dedicated stacking contract exists.
        raise RuntimeError("Promotion-code stacking with tenant overrides is not supported by the current checkout contract.")

    coupon_id = create_stripe_override_coupon(
        override=override,
        list_price_cents=quote["list_price_cents"],
        effective_price_cents=quote["effective_price_cents"],
        product_code=product_code,
    )
    return {**quote, "checkout_required": True, "allow_promotion_codes": False, "coupon_id": coupon_id}
