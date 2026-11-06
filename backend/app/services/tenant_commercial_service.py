from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import or_, select

from app.commercial_override_models import TenantCommercialOverride, TenantPilotSponsorship
from app.models import AdminAuditEvent, Tenant
from app.services.product_license_service import grant_product_entitlement, normalize_product_code

OVERRIDE_TYPES = {"free", "fixed_price", "percent_discount", "amount_discount"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _audit(db, *, actor: str, action: str, target_type: str, target_id: str, details: dict) -> None:
    db.add(
        AdminAuditEvent(
            admin_username=(actor or "system")[:120],
            action=action[:80],
            target_type=target_type[:60],
            target_id=str(target_id)[:120],
            details_json=json.dumps(details, sort_keys=True, default=str),
            created_at_utc=utc_now(),
        )
    )


def _validate_override_values(*, override_type: str, value_number: float, currency: str) -> tuple[str, float, str]:
    kind = (override_type or "").strip().lower()
    if kind not in OVERRIDE_TYPES:
        raise ValueError(f"Unsupported commercial override type: {override_type}")
    value = float(value_number or 0.0)
    normalized_currency = (currency or "EUR").strip().upper()
    if normalized_currency != "EUR":
        raise ValueError("Only EUR commercial overrides are supported.")
    if kind == "free":
        value = 0.0
    elif kind == "fixed_price" and value < 0:
        raise ValueError("Fixed price must be >= 0.")
    elif kind == "percent_discount" and not 0 <= value <= 100:
        raise ValueError("Percent discount must be between 0 and 100.")
    elif kind == "amount_discount" and value < 0:
        raise ValueError("Amount discount must be >= 0.")
    return kind, value, normalized_currency


def create_commercial_override(
    db,
    *,
    tenant_id: str,
    product_code: str,
    override_type: str,
    value_number: float,
    valid_from_utc: datetime,
    valid_until_utc: datetime | None,
    actor: str,
    currency: str = "EUR",
    max_uses: int | None = None,
    reason: str | None = None,
    internal_note: str | None = None,
    allow_promotion_code_stack: bool = False,
) -> TenantCommercialOverride:
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
    if tenant is None:
        raise ValueError("Tenant not found.")
    product = normalize_product_code(product_code)
    if not product:
        raise ValueError("product_code is required.")
    kind, value, normalized_currency = _validate_override_values(
        override_type=override_type,
        value_number=value_number,
        currency=currency,
    )
    start = _as_utc(valid_from_utc)
    end = _as_utc(valid_until_utc)
    if start is None:
        raise ValueError("valid_from_utc is required.")
    if end is not None and end <= start:
        raise ValueError("valid_until_utc must be after valid_from_utc.")
    if max_uses is not None and int(max_uses) <= 0:
        raise ValueError("max_uses must be greater than 0 when specified.")

    candidates = db.scalars(
        select(TenantCommercialOverride).where(
            TenantCommercialOverride.tenant_id == tenant_id,
            TenantCommercialOverride.product_code == product,
            TenantCommercialOverride.status == "active",
        )
    ).all()
    for existing in candidates:
        existing_start = _as_utc(existing.valid_from_utc)
        existing_end = _as_utc(existing.valid_until_utc)
        overlaps = (existing_end is None or existing_end > start) and (end is None or existing_start < end)
        if overlaps:
            raise ValueError("An active commercial override already overlaps this tenant/product validity window.")

    now = utc_now()
    row = TenantCommercialOverride(
        tenant_id=tenant_id,
        product_code=product,
        override_type=kind,
        value_number=value,
        currency=normalized_currency,
        valid_from_utc=start,
        valid_until_utc=end,
        max_uses=int(max_uses) if max_uses is not None else None,
        uses_count=0,
        allow_promotion_code_stack=bool(allow_promotion_code_stack),
        status="active",
        reason=(reason or "").strip() or None,
        internal_note=(internal_note or "").strip() or None,
        created_by=actor,
        updated_by=actor,
        created_at_utc=now,
        updated_at_utc=now,
    )
    db.add(row)
    db.flush()
    _audit(
        db,
        actor=actor,
        action="commercial_override.create",
        target_type="tenant_commercial_override",
        target_id=str(row.id),
        details={
            "tenant_id": tenant_id,
            "product_code": product,
            "override_type": kind,
            "value_number": value,
            "valid_from_utc": start,
            "valid_until_utc": end,
        },
    )
    return row


def revoke_commercial_override(db, *, override_id: int, actor: str, reason: str | None = None) -> TenantCommercialOverride:
    row = db.get(TenantCommercialOverride, override_id)
    if row is None:
        raise ValueError("Commercial override not found.")
    row.status = "revoked"
    row.updated_by = actor
    row.updated_at_utc = utc_now()
    if reason:
        row.internal_note = ((row.internal_note or "") + f"\nRevoked: {reason}").strip()
    _audit(
        db,
        actor=actor,
        action="commercial_override.revoke",
        target_type="tenant_commercial_override",
        target_id=str(row.id),
        details={"tenant_id": row.tenant_id, "product_code": row.product_code, "reason": reason},
    )
    return row


def get_active_commercial_override(db, *, tenant_id: str, product_code: str, at_utc: datetime | None = None) -> TenantCommercialOverride | None:
    moment = _as_utc(at_utc) or utc_now()
    rows = db.scalars(
        select(TenantCommercialOverride).where(
            TenantCommercialOverride.tenant_id == tenant_id,
            TenantCommercialOverride.product_code == normalize_product_code(product_code),
            TenantCommercialOverride.status == "active",
            TenantCommercialOverride.valid_from_utc <= moment,
            or_(
                TenantCommercialOverride.valid_until_utc.is_(None),
                TenantCommercialOverride.valid_until_utc > moment,
            ),
        )
    ).all()
    eligible = [row for row in rows if row.max_uses is None or int(row.uses_count or 0) < int(row.max_uses)]
    if len(eligible) > 1:
        raise RuntimeError("Multiple active commercial overrides found for tenant/product.")
    return eligible[0] if eligible else None


def calculate_effective_price(
    db,
    *,
    tenant_id: str,
    product_code: str,
    list_price_cents: int,
    currency: str = "EUR",
    at_utc: datetime | None = None,
) -> dict:
    base = max(int(list_price_cents or 0), 0)
    normalized_currency = (currency or "EUR").upper()
    if normalized_currency != "EUR":
        raise ValueError("Only EUR pricing is supported.")
    override = get_active_commercial_override(
        db,
        tenant_id=tenant_id,
        product_code=product_code,
        at_utc=at_utc,
    )
    effective = base
    source = "list_price"
    allow_promotion_code = True
    override_id = None
    override_type = None
    if override is not None:
        override_id = override.id
        override_type = override.override_type
        source = "tenant_commercial_override"
        allow_promotion_code = bool(override.allow_promotion_code_stack)
        value = float(override.value_number or 0.0)
        if override.override_type == "free":
            effective = 0
        elif override.override_type == "fixed_price":
            effective = max(int(round(value * 100)), 0)
        elif override.override_type == "percent_discount":
            effective = max(int(round(base * (1 - value / 100.0))), 0)
        elif override.override_type == "amount_discount":
            effective = max(base - int(round(value * 100)), 0)
        else:
            raise RuntimeError("Unsupported persisted commercial override type.")

    return {
        "tenant_id": tenant_id,
        "product_code": normalize_product_code(product_code),
        "currency": normalized_currency,
        "list_price_cents": base,
        "effective_price_cents": effective,
        "effective_price_eur": round(effective / 100, 2),
        "price_source": source,
        "override_id": override_id,
        "override_type": override_type,
        "promotion_code_allowed": allow_promotion_code,
    }


def consume_override_use(db, *, override_id: int, actor: str = "checkout") -> TenantCommercialOverride:
    row = db.get(TenantCommercialOverride, override_id)
    if row is None or row.status != "active":
        raise ValueError("Commercial override is not active.")
    if row.max_uses is not None and int(row.uses_count or 0) >= int(row.max_uses):
        raise ValueError("Commercial override has no uses remaining.")
    row.uses_count = int(row.uses_count or 0) + 1
    row.updated_by = actor
    row.updated_at_utc = utc_now()
    _audit(
        db,
        actor=actor,
        action="commercial_override.consume",
        target_type="tenant_commercial_override",
        target_id=str(row.id),
        details={"uses_count": row.uses_count, "max_uses": row.max_uses},
    )
    return row


def grant_pilot_sponsorship(
    db,
    *,
    tenant_id: str,
    product_code: str,
    valid_from_utc: datetime,
    valid_until_utc: datetime,
    actor: str,
    reason: str,
) -> TenantPilotSponsorship:
    start = _as_utc(valid_from_utc)
    end = _as_utc(valid_until_utc)
    if start is None or end is None or end <= start:
        raise ValueError("Pilot sponsorship requires a valid start/end window.")
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
    if tenant is None:
        raise ValueError("Tenant not found.")
    product = normalize_product_code(product_code)
    now = utc_now()
    sponsorship = TenantPilotSponsorship(
        tenant_id=tenant_id,
        product_code=product,
        valid_from_utc=start,
        valid_until_utc=end,
        status="active",
        reason=reason.strip(),
        created_by=actor,
        created_at_utc=now,
        updated_at_utc=now,
    )
    db.add(sponsorship)
    db.flush()
    grant_product_entitlement(
        db,
        tenant_id=tenant_id,
        product_code=product,
        source=f"pilot_sponsorship:{sponsorship.id}",
        valid_until_utc=end,
    )
    _audit(
        db,
        actor=actor,
        action="pilot_sponsorship.create",
        target_type="tenant_pilot_sponsorship",
        target_id=str(sponsorship.id),
        details={
            "tenant_id": tenant_id,
            "product_code": product,
            "valid_from_utc": start,
            "valid_until_utc": end,
            "reason": reason,
        },
    )
    return sponsorship
