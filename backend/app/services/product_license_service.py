from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from app.models import (
    Subscription,
    Tenant,
    TenantProductEntitlement,
    TenantProductPurchase,
    TenantScanCredit,
)

PRODUCT_ASSESSMENT = "assessment"
PRODUCT_VALIDATION_CHECK = "validation_check"
PRODUCT_MONITORING_MONTHLY = "monitoring_monthly"
PRODUCT_MONITORING_ANNUAL = "monitoring_annual"
PRODUCT_LEGACY_PREMIUM = "premium"

PRODUCT_ALIASES = {
    "data_health_check": PRODUCT_ASSESSMENT,
    "bcsentinel_assessment": PRODUCT_ASSESSMENT,
    "assessment": PRODUCT_ASSESSMENT,
    "follow_up_scan": PRODUCT_VALIDATION_CHECK,
    "validation": PRODUCT_VALIDATION_CHECK,
    "validation_check": PRODUCT_VALIDATION_CHECK,
    "bcsentinel_validation_check": PRODUCT_VALIDATION_CHECK,
    "monitoring": PRODUCT_MONITORING_MONTHLY,
    "monitoring_monthly": PRODUCT_MONITORING_MONTHLY,
    "bcsentinel_monitoring_monthly": PRODUCT_MONITORING_MONTHLY,
    "monitoring_annual": PRODUCT_MONITORING_ANNUAL,
    "monitoring_yearly": PRODUCT_MONITORING_ANNUAL,
    "bcsentinel_monitoring_annual": PRODUCT_MONITORING_ANNUAL,
    "premium": PRODUCT_MONITORING_MONTHLY,
}

ONE_TIME_PRODUCTS = {PRODUCT_ASSESSMENT, PRODUCT_VALIDATION_CHECK}
MONITORING_PRODUCTS = {PRODUCT_MONITORING_MONTHLY, PRODUCT_MONITORING_ANNUAL, PRODUCT_LEGACY_PREMIUM}

PRODUCT_DISPLAY_NAMES = {
    PRODUCT_ASSESSMENT: "BCSentinel Assessment",
    PRODUCT_VALIDATION_CHECK: "BCSentinel Validation Check",
    PRODUCT_MONITORING_MONTHLY: "BCSentinel Monitoring Monthly",
    PRODUCT_MONITORING_ANNUAL: "BCSentinel Monitoring Annual",
    PRODUCT_LEGACY_PREMIUM: "Legacy Premium",
}

PRODUCT_PRICES_EUR = {
    PRODUCT_ASSESSMENT: 79.0,
    PRODUCT_VALIDATION_CHECK: 49.0,
    PRODUCT_MONITORING_MONTHLY: 99.0,
    PRODUCT_MONITORING_ANNUAL: 990.0,
}

BASE_FEATURES = {
    "scan_sync",
    "quick_scan",
    "billing_checkout",
}

PAID_SCAN_FEATURES = BASE_FEATURES | {
    "deep_scan",
    "executive_report",
    "analytics_single_scan",
    "recommendations",
}

MONITORING_FEATURES = PAID_SCAN_FEATURES | {
    "monitoring_active",
    "analytics_full",
    "scan_history",
    "scan_trend",
    "billing_portal",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_product_code(value: str | None, *, billing_interval: str | None = None) -> str:
    normalized = (value or "").strip().lower()
    if not normalized:
        normalized = PRODUCT_MONITORING_ANNUAL if (billing_interval or "").strip().lower() == "yearly" else PRODUCT_ASSESSMENT
    resolved = PRODUCT_ALIASES.get(normalized)
    if resolved:
        return resolved
    return normalized


def is_one_time_product(product_code: str) -> bool:
    return normalize_product_code(product_code) in ONE_TIME_PRODUCTS


def is_monitoring_product(product_code: str) -> bool:
    return normalize_product_code(product_code) in MONITORING_PRODUCTS


def scan_credit_count(db, tenant_id: str) -> int:
    return int(
        db.query(TenantScanCredit)
        .filter(TenantScanCredit.tenant_id == tenant_id, TenantScanCredit.status == "available")
        .count()
    )


def active_entitlement_product_codes(db, tenant_id: str) -> list[str]:
    now = utc_now()
    rows = db.scalars(
        select(TenantProductEntitlement).where(
            TenantProductEntitlement.tenant_id == tenant_id,
            TenantProductEntitlement.status == "active",
        )
    ).all()
    product_codes = []
    for row in rows:
        if row.valid_until_utc is not None and row.valid_until_utc < now:
            continue
        product_codes.append(normalize_product_code(row.product_code))
    return sorted(set(product_codes))


def has_active_monitoring_subscription(db, tenant: Tenant) -> bool:
    if (tenant.current_plan or "").strip().lower() == "premium" and (tenant.license_status or "").strip().lower() in {"trial", "active"}:
        return True

    subscriptions = db.scalars(
        select(Subscription).where(Subscription.tenant_id == tenant.tenant_id)
    ).all()
    for subscription in subscriptions:
        if (subscription.status or "").strip().lower() not in {"trialing", "active"}:
            continue
        if normalize_product_code(subscription.plan_code) in MONITORING_PRODUCTS:
            return True
    return False


def resolve_product_features(db, tenant: Tenant) -> set[str]:
    features = set(BASE_FEATURES)
    if scan_credit_count(db, tenant.tenant_id) > 0:
        features.update(PAID_SCAN_FEATURES)

    product_codes = set(active_entitlement_product_codes(db, tenant.tenant_id))
    if product_codes.intersection(MONITORING_PRODUCTS) or has_active_monitoring_subscription(db, tenant):
        features.update(MONITORING_FEATURES)
    elif product_codes.intersection(ONE_TIME_PRODUCTS):
        features.update(PAID_SCAN_FEATURES)

    return features


def grant_scan_credit(
    db,
    *,
    tenant_id: str,
    product_code: str,
    source: str = "manual",
    source_purchase_id: int | None = None,
) -> TenantScanCredit:
    credit = TenantScanCredit(
        tenant_id=tenant_id,
        product_code=normalize_product_code(product_code),
        status="available",
        source=source,
        source_purchase_id=source_purchase_id,
        created_at_utc=utc_now(),
    )
    db.add(credit)
    db.flush()
    return credit


def grant_product_entitlement(
    db,
    *,
    tenant_id: str,
    product_code: str,
    source: str = "manual",
    valid_until_utc: datetime | None = None,
) -> TenantProductEntitlement:
    now = utc_now()
    entitlement = TenantProductEntitlement(
        tenant_id=tenant_id,
        product_code=normalize_product_code(product_code),
        status="active",
        source=source,
        valid_until_utc=valid_until_utc,
        created_at_utc=now,
        updated_at_utc=now,
    )
    db.add(entitlement)
    db.flush()
    return entitlement


def record_product_purchase(
    db,
    *,
    tenant_id: str,
    product_code: str,
    provider: str,
    provider_checkout_session_id: str | None,
    provider_payment_intent_id: str | None,
    status: str,
    currency: str,
    amount_total: float,
    source: str = "checkout",
) -> TenantProductPurchase:
    existing = None
    if provider_checkout_session_id:
        existing = db.scalar(
            select(TenantProductPurchase).where(
                TenantProductPurchase.provider_checkout_session_id == provider_checkout_session_id
            )
        )
    now = utc_now()
    if existing is None:
        existing = TenantProductPurchase(
            tenant_id=tenant_id,
            product_code=normalize_product_code(product_code),
            provider=provider,
            provider_checkout_session_id=provider_checkout_session_id,
            provider_payment_intent_id=provider_payment_intent_id,
            status=status,
            currency=(currency or "EUR").upper(),
            amount_total=float(amount_total or 0.0),
            source=source,
            created_at_utc=now,
            updated_at_utc=now,
        )
        db.add(existing)
        db.flush()
        return existing

    existing.product_code = normalize_product_code(product_code)
    existing.status = status
    existing.currency = (currency or "EUR").upper()
    existing.amount_total = float(amount_total or 0.0)
    existing.provider_payment_intent_id = provider_payment_intent_id
    existing.updated_at_utc = now
    return existing


def consume_scan_credit_for_scan(db, *, tenant_id: str, scan_id: str) -> TenantScanCredit | None:
    existing = db.scalar(
        select(TenantScanCredit).where(
            TenantScanCredit.tenant_id == tenant_id,
            TenantScanCredit.consumed_scan_id == scan_id,
        )
    )
    if existing is not None:
        return existing

    credit = db.scalar(
        select(TenantScanCredit)
        .where(TenantScanCredit.tenant_id == tenant_id, TenantScanCredit.status == "available")
        .order_by(TenantScanCredit.created_at_utc.asc(), TenantScanCredit.id.asc())
        .limit(1)
    )
    if credit is None:
        return None

    credit.status = "consumed"
    credit.consumed_scan_id = scan_id
    credit.consumed_at_utc = utc_now()
    return credit


def build_license_snapshot(db, tenant: Tenant) -> dict[str, Any]:
    features = sorted(resolve_product_features(db, tenant))
    active_products = active_entitlement_product_codes(db, tenant.tenant_id)
    if has_active_monitoring_subscription(db, tenant):
        active_products = sorted(set(active_products + [PRODUCT_MONITORING_MONTHLY]))
    credits_available = scan_credit_count(db, tenant.tenant_id)
    return {
        "features": features,
        "active_products": active_products,
        "scan_credits_available": credits_available,
        "monitoring_active": "monitoring_active" in features,
        "products": [
            {
                "product_code": code,
                "display_name": PRODUCT_DISPLAY_NAMES.get(code, code),
                "price_eur": PRODUCT_PRICES_EUR.get(code, 0.0),
                "active": code in active_products,
            }
            for code in [
                PRODUCT_ASSESSMENT,
                PRODUCT_VALIDATION_CHECK,
                PRODUCT_MONITORING_MONTHLY,
                PRODUCT_MONITORING_ANNUAL,
            ]
        ],
    }
