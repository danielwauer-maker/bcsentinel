"""Commercial-session checkout is not released.

The experimental pricing/Stripe implementation referenced helpers absent from the
current core billing contract. Keep its public route explicit and fail-closed,
even if the reserved feature flag is mistakenly enabled, until a separate
reviewed implementation can provide complete payment and refund lifecycle.
Historical billing endpoints are intentionally not changed.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.routers.billing import CheckoutSessionRequest
from app.security.tenant import require_tenant_headers

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
    """No commercial session, quote, Stripe coupon or charge may be created."""
    raise HTTPException(status_code=503, detail="Commercial checkout is not released.")
