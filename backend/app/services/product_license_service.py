from __future__ import annotations

import calendar
from datetime import datetime, time, timedelta, timezone
from typing import Any

from sqlalchemy import select

from app.models import (
    CreditLedgerEntry,
    Scan,
    ScanRunStatus,
    ScanStartRequest,
    Subscription,
    Tenant,
    TenantProductEntitlement,
    TenantProductPurchase,
    TenantScanCredit,
)

PRODUCT_DATA_HEALTH_SCORE = "data_health_score"
PRODUCT_FULL_ANALYSIS = "full_analysis"
PRODUCT_ASSESSMENT = PRODUCT_FULL_ANALYSIS
PRODUCT_ASSESSMENT_LEGACY = "assessment"
PRODUCT_VALIDATION_CHECK = "validation_check"
PRODUCT_MONITORING_MONTHLY = "monitoring_monthly"
PRODUCT_MONITORING_ANNUAL = "monitoring_annual"

PRODUCT_ALIASES = {
    # assessment is the legacy code for the first paid 7-day access product.
    "assessment": PRODUCT_FULL_ANALYSIS,
    "full_analysis": PRODUCT_FULL_ANALYSIS,
    "data_health_score": PRODUCT_DATA_HEALTH_SCORE,
    "validation_check": PRODUCT_VALIDATION_CHECK,
    "monitoring_monthly": PRODUCT_MONITORING_MONTHLY,
    "monitoring_annual": PRODUCT_MONITORING_ANNUAL,
}

ONE_TIME_PRODUCTS = {PRODUCT_FULL_ANALYSIS, PRODUCT_VALIDATION_CHECK}
MONITORING_PRODUCTS = {PRODUCT_MONITORING_MONTHLY, PRODUCT_MONITORING_ANNUAL}
PRODUCT_CODES = {
    PRODUCT_DATA_HEALTH_SCORE,
    PRODUCT_FULL_ANALYSIS,
    PRODUCT_VALIDATION_CHECK,
    PRODUCT_MONITORING_MONTHLY,
    PRODUCT_MONITORING_ANNUAL,
}
LEGACY_PRODUCT_CODES = {PRODUCT_ASSESSMENT_LEGACY}

PRODUCT_DISPLAY_NAMES = {
    PRODUCT_DATA_HEALTH_SCORE: "BCSentinel Data Health Score",
    PRODUCT_FULL_ANALYSIS: "BCSentinel Full Analysis",
    PRODUCT_VALIDATION_CHECK: "BCSentinel Validation Check",
    PRODUCT_MONITORING_MONTHLY: "BCSentinel Monitoring Monthly",
    PRODUCT_MONITORING_ANNUAL: "BCSentinel Monitoring Annual",
}

PRICING_TIERS = (
    ("starter", 100_000),
    ("professional", 250_000),
    ("business", 500_000),
    ("enterprise", None),
)

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

ONE_TIME_ACCESS_DAYS = 7


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _end_of_day_utc(value: datetime | None) -> datetime | None:
    normalized = _as_utc(value)
    if normalized is None:
        return None
    return datetime.combine(normalized.date(), time(23, 59), tzinfo=timezone.utc)


def _add_months(value: datetime, months: int) -> datetime:
    normalized = _as_utc(value) or utc_now()
    month_index = normalized.month - 1 + months
    year = normalized.year + month_index // 12
    month = month_index % 12 + 1
    day = min(normalized.day, calendar.monthrange(year, month)[1])
    return normalized.replace(year=year, month=month, day=day)


def calculate_product_access_until(product_code: str, anchor: datetime | None = None) -> datetime | None:
    normalized_product = normalize_product_code(product_code)
    start = _as_utc(anchor) or utc_now()
    if normalized_product in ONE_TIME_PRODUCTS:
        return calculate_access_window_until(days=ONE_TIME_ACCESS_DAYS, anchor=start)
    if normalized_product == PRODUCT_MONITORING_MONTHLY:
        return _end_of_day_utc(_add_months(start, 1))
    if normalized_product == PRODUCT_MONITORING_ANNUAL:
        return _end_of_day_utc(_add_months(start, 12))
    return None


def calculate_access_window_until(*, days: int, anchor: datetime | None = None) -> datetime:
    start = _as_utc(anchor) or utc_now()
    return start + timedelta(days=max(int(days or 0), 0))


def extend_tenant_premium_access(db, *, tenant_id: str, anchor: datetime | None = None) -> datetime:
    """Apply the normative max(existing, purchase/grant time + 7 days) rule."""
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id).with_for_update())
    if tenant is None:
        raise ValueError("Tenant not found while extending premium access.")
    candidate = calculate_access_window_until(days=ONE_TIME_ACCESS_DAYS, anchor=anchor)
    tenant.premium_until_utc = _max_datetime([tenant.premium_until_utc, candidate])
    db.flush()
    return _as_utc(tenant.premium_until_utc) or candidate


def _iso(value: datetime | None) -> str | None:
    normalized = _as_utc(value)
    if normalized is None:
        return None
    return normalized.isoformat().replace("+00:00", "Z")


def _bc_datetime(value: datetime | None) -> str | None:
    normalized = _as_utc(value)
    if normalized is None:
        return None
    return normalized.strftime("%Y-%m-%dT%H:%M:%S")


def _max_datetime(values: list[datetime | None]) -> datetime | None:
    normalized = [_as_utc(value) for value in values if value is not None]
    if not normalized:
        return None
    return max(normalized)


def normalize_product_code(value: str | None, *, billing_interval: str | None = None) -> str:
    normalized = (value or "").strip().lower()
    if not normalized:
        return ""
    resolved = PRODUCT_ALIASES.get(normalized)
    if resolved:
        return resolved
    return normalized


def product_code_storage_aliases(product_code: str) -> set[str]:
    normalized = normalize_product_code(product_code)
    aliases = {normalized}
    if normalized == PRODUCT_FULL_ANALYSIS:
        aliases.add(PRODUCT_ASSESSMENT_LEGACY)
    return aliases


def pricing_tier_for_record_count(record_count: int | None) -> str | None:
    if record_count is None:
        return None
    normalized_count = max(int(record_count or 0), 0)
    if normalized_count <= 100_000:
        return "starter"
    if normalized_count <= 250_000:
        return "professional"
    if normalized_count <= 500_000:
        return "business"
    return "enterprise"


def is_one_time_product(product_code: str) -> bool:
    return normalize_product_code(product_code) in ONE_TIME_PRODUCTS


def is_monitoring_product(product_code: str) -> bool:
    return normalize_product_code(product_code) in MONITORING_PRODUCTS


def scan_credit_count(db, tenant_id: str) -> int:
    return int(
        db.query(TenantScanCredit)
        .filter(
            TenantScanCredit.tenant_id == tenant_id,
            TenantScanCredit.status == "available",
            TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
        )
        .count()
    )


def scan_credit_count_for_product(db, tenant_id: str, product_code: str) -> int:
    return int(
        db.query(TenantScanCredit)
        .filter(
            TenantScanCredit.tenant_id == tenant_id,
            TenantScanCredit.status == "available",
            TenantScanCredit.product_code.in_(sorted(product_code_storage_aliases(product_code))),
        )
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
        valid_until = _end_of_day_utc(row.valid_until_utc)
        if valid_until is not None and valid_until < now:
            continue
        product_codes.append(normalize_product_code(row.product_code))
    return sorted(set(product_codes))


def _latest_scan_record_count(db, tenant_id: str) -> int | None:
    scan = db.scalar(
        select(Scan)
        .where(Scan.tenant_id == tenant_id)
        .order_by(Scan.generated_at_utc.desc(), Scan.id.desc())
        .limit(1)
    )
    if scan is None:
        return None
    try:
        return max(int(scan.total_records or 0), 0)
    except (TypeError, ValueError):
        return None


def _tenant_has_scan_results(db, tenant_id: str) -> bool:
    return db.scalar(select(Scan.id).where(Scan.tenant_id == tenant_id).limit(1)) is not None


def _completed_data_health_score_at(db, tenant_id: str) -> datetime | None:
    """Return the authoritative completion anchor for the tenant's free scan."""
    return _as_utc(
        db.scalar(
            select(ScanRunStatus.completed_at_utc)
            .join(ScanStartRequest, ScanStartRequest.scan_id == ScanRunStatus.run_id)
            .join(Scan, Scan.scan_id == ScanRunStatus.run_id)
            .where(
                ScanRunStatus.tenant_id == tenant_id,
                ScanRunStatus.status.in_(["completed", "completed_with_warnings"]),
                ScanRunStatus.completed_at_utc.is_not(None),
                ScanRunStatus.result_persisted_at_utc.is_not(None),
                ScanStartRequest.tenant_id == tenant_id,
                ScanStartRequest.resolved_product_code == PRODUCT_DATA_HEALTH_SCORE,
                ScanStartRequest.free_scan_slot == PRODUCT_DATA_HEALTH_SCORE,
                Scan.tenant_id == tenant_id,
            )
            .order_by(ScanRunStatus.completed_at_utc.desc())
            .limit(1)
        )
    )


def _free_access_until(db, tenant_id: str) -> datetime | None:
    completed_at = _completed_data_health_score_at(db, tenant_id)
    if completed_at is None:
        return None
    return calculate_access_window_until(days=ONE_TIME_ACCESS_DAYS, anchor=completed_at)


def _has_legacy_premium_access(tenant: Tenant) -> bool:
    plan = (tenant.current_plan or "").strip().lower()
    status = (tenant.license_status or "").strip().lower()
    return plan == "premium" and status in {"trial", "active"}


def _has_monitoring_records(db, tenant_id: str) -> bool:
    subscriptions = db.scalars(
        select(Subscription).where(Subscription.tenant_id == tenant_id)
    ).all()
    for subscription in subscriptions:
        if normalize_product_code(subscription.plan_code) in MONITORING_PRODUCTS:
            return True

    entitlements = db.scalars(
        select(TenantProductEntitlement).where(TenantProductEntitlement.tenant_id == tenant_id)
    ).all()
    for entitlement in entitlements:
        if normalize_product_code(entitlement.product_code) in MONITORING_PRODUCTS:
            return True

    return False


def _one_time_access_until_for_product(db, tenant_id: str, product_code: str) -> datetime | None:
    normalized_product = normalize_product_code(product_code)
    storage_aliases = product_code_storage_aliases(normalized_product)
    access_until_values: list[datetime | None] = []

    credits = db.scalars(
        select(TenantScanCredit).where(
            TenantScanCredit.tenant_id == tenant_id,
            TenantScanCredit.product_code.in_(storage_aliases),
            TenantScanCredit.status.in_(["available", "consumed"]),
        )
    ).all()
    for credit in credits:
        anchor = credit.consumed_at_utc if credit.consumed_at_utc is not None else credit.created_at_utc
        anchor = _as_utc(anchor)
        if anchor is not None:
            access_until_values.append(calculate_product_access_until(normalized_product, anchor))

    purchases = db.scalars(
        select(TenantProductPurchase).where(
            TenantProductPurchase.tenant_id == tenant_id,
            TenantProductPurchase.product_code.in_(storage_aliases),
            TenantProductPurchase.status.in_(["paid", "complete", "completed"]),
        )
    ).all()
    for purchase in purchases:
        anchor = _as_utc(purchase.created_at_utc)
        if anchor is not None:
            access_until_values.append(calculate_product_access_until(normalized_product, anchor))

    entitlements = db.scalars(
        select(TenantProductEntitlement).where(
            TenantProductEntitlement.tenant_id == tenant_id,
            TenantProductEntitlement.product_code.in_(storage_aliases),
            TenantProductEntitlement.status == "active",
        )
    ).all()
    for entitlement in entitlements:
        if entitlement.valid_until_utc is None:
            access_until_values.append(calculate_product_access_until(normalized_product))
        else:
            access_until_values.append(_as_utc(entitlement.valid_until_utc))

    return _max_datetime(access_until_values)


def _monitoring_access_until(db, tenant: Tenant) -> datetime | None:
    values: list[datetime | None] = []
    subscriptions = db.scalars(
        select(Subscription).where(Subscription.tenant_id == tenant.tenant_id)
    ).all()
    for subscription in subscriptions:
        if (subscription.status or "").strip().lower() not in {"trialing", "active"}:
            continue
        product_code = normalize_product_code(subscription.plan_code)
        if product_code in MONITORING_PRODUCTS:
            period_end = _end_of_day_utc(subscription.current_period_end_utc)
            if period_end is None:
                anchor = (
                    _as_utc(subscription.current_period_start_utc)
                    or _as_utc(subscription.created_at_utc)
                    or _as_utc(subscription.updated_at_utc)
                    or utc_now()
                )
                period_end = calculate_product_access_until(product_code, anchor)
            values.append(period_end)

    entitlements = db.scalars(
        select(TenantProductEntitlement).where(
            TenantProductEntitlement.tenant_id == tenant.tenant_id,
            TenantProductEntitlement.status == "active",
        )
    ).all()
    for entitlement in entitlements:
        product_code = normalize_product_code(entitlement.product_code)
        if product_code in MONITORING_PRODUCTS:
            valid_until = _end_of_day_utc(entitlement.valid_until_utc)
            if valid_until is None:
                anchor = _as_utc(entitlement.created_at_utc) or _as_utc(entitlement.updated_at_utc) or utc_now()
                valid_until = calculate_product_access_until(product_code, anchor)
            values.append(valid_until)

    if has_active_monitoring_subscription(db, tenant) and not values:
        return calculate_product_access_until(PRODUCT_MONITORING_MONTHLY, utc_now())
    return _max_datetime(values)


def build_product_access_snapshot(db, tenant: Tenant) -> dict[str, Any]:
    now = utc_now()
    free_access_until = _free_access_until(db, tenant.tenant_id)
    full_analysis_until = _one_time_access_until_for_product(db, tenant.tenant_id, PRODUCT_FULL_ANALYSIS)
    validation_until = _one_time_access_until_for_product(db, tenant.tenant_id, PRODUCT_VALIDATION_CHECK)
    monitoring_until = _monitoring_access_until(db, tenant)
    monitoring_active = has_active_monitoring_subscription(db, tenant) or (
        monitoring_until is not None and monitoring_until >= now
    )

    explicit_premium_until = _as_utc(tenant.premium_until_utc)
    one_time_until = _max_datetime([explicit_premium_until, full_analysis_until, validation_until])
    premium_access_until = None if monitoring_active and monitoring_until is None else _max_datetime([one_time_until, monitoring_until])
    full_analysis_active = full_analysis_until is not None and full_analysis_until >= now
    validation_active = validation_until is not None and validation_until >= now
    one_time_active = one_time_until is not None and one_time_until >= now
    premium_access_active = monitoring_active or one_time_active
    free_access_active = free_access_until is not None and free_access_until >= now
    protected_access_until = _max_datetime([premium_access_until, free_access_until])
    protected_access_active = premium_access_active or free_access_active
    credits_available = scan_credit_count(db, tenant.tenant_id)
    assessment_credits_available = scan_credit_count_for_product(db, tenant.tenant_id, PRODUCT_FULL_ANALYSIS)
    validation_credits_available = scan_credit_count_for_product(db, tenant.tenant_id, PRODUCT_VALIDATION_CHECK)
    has_scan_results = _tenant_has_scan_results(db, tenant.tenant_id)
    free_assessment_used = bool(tenant.free_assessment_used) or free_access_until is not None
    has_completed_data_health_score = free_access_until is not None
    record_count = _latest_scan_record_count(db, tenant.tenant_id)
    pricing_tier = pricing_tier_for_record_count(record_count)

    return {
        "free_assessment_used": free_assessment_used,
        "free_assessment_available": not free_assessment_used,
        "premium_active": premium_access_active,
        "premium_until": _iso(one_time_until),
        "validation_credits": validation_credits_available,
        "monitoring_until": _iso(monitoring_until),
        "dataset_tier": pricing_tier,
        "capabilities": {
            "free_dashboard": free_access_active,
            "full_dashboard": premium_access_active,
            "findings_full": premium_access_active,
            "issues": premium_access_active,
            "actions": premium_access_active,
            "executive_report_full": premium_access_active,
            "monitoring": monitoring_active,
            "manual_scan": monitoring_active or validation_credits_available > 0 or not free_assessment_used,
        },
        "can_run_data_health_score": not free_assessment_used,
        "has_completed_data_health_score": has_completed_data_health_score,
        "can_view_free_insights": protected_access_active and has_scan_results,
        "can_view_issues": protected_access_active,
        "can_view_actions": premium_access_active,
        "can_view_reports": protected_access_active,
        "can_view_record_details": premium_access_active,
        "can_use_monitoring": monitoring_active,
        "full_analysis_access_active": full_analysis_active,
        "validation_check_access_active": validation_active,
        "premium_access_until": _iso(premium_access_until),
        "premium_access_until_bc": _bc_datetime(premium_access_until),
        "product_access_until": _iso(premium_access_until),
        "subscription_end": _iso(monitoring_until if monitoring_active else premium_access_until),
        "subscription_end_bc": _bc_datetime(monitoring_until if monitoring_active else premium_access_until),
        "subscription_end_utc": _iso(monitoring_until if monitoring_active else premium_access_until),
        "record_count": record_count,
        "pricing_tier": pricing_tier,
        "assessment_access_active": full_analysis_active,
        "validation_access_active": validation_active,
        "monitoring_active": monitoring_active,
        "dashboard_access_until": _iso(protected_access_until),
        "dashboard_access_until_bc": _bc_datetime(protected_access_until),
        "issue_access_until": _iso(protected_access_until),
        "issue_access_until_bc": _bc_datetime(protected_access_until),
        "report_access_until": _iso(protected_access_until),
        "can_run_deep_scan": monitoring_active or validation_credits_available > 0,
        "can_view_dashboard": protected_access_active,
        "can_view_issue_details": protected_access_active,
        "can_view_executive_report": protected_access_active,
        "scan_credits_available": validation_credits_available,
        "assessment_scan_credits_available": 0,
        "validation_scan_credits_available": validation_credits_available,
        "access_model": "monitoring" if monitoring_active else ("one_time" if one_time_active else ("free" if free_access_active else "none")),
        "free_access_until": _iso(free_access_until),
        "assessment_access_until": _iso(full_analysis_until),
        "full_analysis_access_until": _iso(full_analysis_until),
        "validation_access_until": _iso(validation_until),
        "validation_check_access_until": _iso(validation_until),
        "monitoring_access_until": _iso(monitoring_until),
        "monitoring_access_until_bc": _bc_datetime(monitoring_until),
        "monitoring_period_end": _iso(monitoring_until),
        "monitoring_period_end_bc": _bc_datetime(monitoring_until),
    }


def has_active_monitoring_subscription(db, tenant: Tenant) -> bool:
    subscriptions = db.scalars(
        select(Subscription).where(Subscription.tenant_id == tenant.tenant_id)
    ).all()
    for subscription in subscriptions:
        if (subscription.status or "").strip().lower() not in {"trialing", "active"}:
            continue
        if normalize_product_code(subscription.plan_code) in MONITORING_PRODUCTS:
            period_end = _end_of_day_utc(subscription.current_period_end_utc)
            if period_end is not None and period_end < utc_now():
                continue
            return True
    return False


def active_monitoring_subscription_product_codes(db, tenant: Tenant) -> list[str]:
    product_codes: list[str] = []
    subscriptions = db.scalars(
        select(Subscription).where(Subscription.tenant_id == tenant.tenant_id)
    ).all()
    for subscription in subscriptions:
        if (subscription.status or "").strip().lower() not in {"trialing", "active"}:
            continue
        product_code = normalize_product_code(subscription.plan_code)
        period_end = _end_of_day_utc(subscription.current_period_end_utc)
        if product_code in MONITORING_PRODUCTS and (period_end is None or period_end >= utc_now()):
            product_codes.append(product_code)
    return sorted(set(product_codes))


def resolve_product_features(db, tenant: Tenant) -> set[str]:
    features = set(BASE_FEATURES)
    access = build_product_access_snapshot(db, tenant)
    if access["can_run_deep_scan"] or access["premium_active"]:
        features.update(PAID_SCAN_FEATURES)

    product_codes = set(active_entitlement_product_codes(db, tenant.tenant_id))
    if product_codes.intersection(MONITORING_PRODUCTS) or access["monitoring_active"]:
        features.update(MONITORING_FEATURES)
    elif product_codes.intersection(ONE_TIME_PRODUCTS):
        features.update(PAID_SCAN_FEATURES)

    has_provider_subscription = (
        db.scalar(
            select(Subscription.id).where(
                Subscription.tenant_id == tenant.tenant_id,
                Subscription.provider_subscription_id.is_not(None),
                Subscription.status.in_(["trialing", "active", "past_due", "incomplete"]),
            )
        )
        is not None
    )
    if has_provider_subscription:
        features.add("billing_portal")

    return features


def grant_scan_credit(
    db,
    *,
    tenant_id: str,
    product_code: str,
    source: str = "manual",
    source_purchase_id: int | None = None,
) -> TenantScanCredit:
    normalized_product = normalize_product_code(product_code)
    if normalized_product != PRODUCT_VALIDATION_CHECK:
        raise ValueError("Only Validation Check may grant a scan credit.")
    credit = TenantScanCredit(
        tenant_id=tenant_id,
        product_code=normalized_product,
        status="available",
        source=source,
        source_purchase_id=source_purchase_id,
        created_at_utc=utc_now(),
    )
    db.add(credit)
    db.flush()
    operation = "MANUAL_ADJUSTMENT" if source.startswith("admin") else "PURCHASE_GRANTED"
    db.add(
        CreditLedgerEntry(
            tenant_id=tenant_id,
            credit_id=credit.id,
            source_purchase_id=source_purchase_id,
            product_code=credit.product_code,
            operation_type=operation,
            amount=1,
            balance_after=scan_credit_count(db, tenant_id),
            reason="Manual credit grant" if operation == "MANUAL_ADJUSTMENT" else "Credit granted from completed purchase",
            created_at_utc=utc_now(),
        )
    )
    extend_tenant_premium_access(db, tenant_id=tenant_id)
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
    if normalize_product_code(product_code) in ONE_TIME_PRODUCTS:
        entitlement.valid_until_utc = extend_tenant_premium_access(db, tenant_id=tenant_id)
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


def build_license_snapshot(db, tenant: Tenant) -> dict[str, Any]:
    from app.services.product_pricing_service import ensure_default_product_pricing, list_product_pricing

    features = sorted(resolve_product_features(db, tenant))
    active_products = active_entitlement_product_codes(db, tenant.tenant_id)
    ensure_default_product_pricing(db)
    product_price_map = {
        row.product_key: round(max(int(row.price_cents or 0), 0) / 100, 2)
        for row in list_product_pricing(db)
    }
    access = build_product_access_snapshot(db, tenant)
    if access["full_analysis_access_active"]:
        active_products = sorted(set(active_products + [PRODUCT_FULL_ANALYSIS]))
    if access["validation_access_active"]:
        active_products = sorted(set(active_products + [PRODUCT_VALIDATION_CHECK]))
    active_products = sorted(set(active_products + active_monitoring_subscription_product_codes(db, tenant)))
    return {
        "features": features,
        "active_products": active_products,
        "scan_credits_available": access["scan_credits_available"],
        "assessment_scan_credits_available": access["assessment_scan_credits_available"],
        "validation_scan_credits_available": access["validation_scan_credits_available"],
        "monitoring_active": access["monitoring_active"],
        "product_access": access,
        "assessment_access_active": access["assessment_access_active"],
        "full_analysis_access_active": access["full_analysis_access_active"],
        "validation_access_active": access["validation_access_active"],
        "validation_check_access_active": access["validation_check_access_active"],
        "dashboard_access_until": access["dashboard_access_until"],
        "issue_access_until": access["issue_access_until"],
        "premium_access_until": access["premium_access_until"],
        "premium_access_until_bc": access["premium_access_until_bc"],
        "product_access_until": access["product_access_until"],
        "subscription_end": access["subscription_end"],
        "subscription_end_bc": access["subscription_end_bc"],
        "subscription_end_utc": access["subscription_end_utc"],
        "monitoring_access_until": access["monitoring_access_until"],
        "monitoring_access_until_bc": access["monitoring_access_until_bc"],
        "monitoring_period_end": access["monitoring_period_end"],
        "monitoring_period_end_bc": access["monitoring_period_end_bc"],
        "dashboard_access_until_bc": access["dashboard_access_until_bc"],
        "issue_access_until_bc": access["issue_access_until_bc"],
        "can_run_deep_scan": access["can_run_deep_scan"],
        "can_view_dashboard": access["can_view_dashboard"],
        "can_view_issue_details": access["can_view_issue_details"],
        "can_view_free_insights": access["can_view_free_insights"],
        "can_run_data_health_score": access["can_run_data_health_score"],
        "has_completed_data_health_score": access["has_completed_data_health_score"],
        "can_view_issues": access["can_view_issues"],
        "can_view_actions": access["can_view_actions"],
        "can_view_reports": access["can_view_reports"],
        "can_view_record_details": access["can_view_record_details"],
        "can_use_monitoring": access["can_use_monitoring"],
        "record_count": access["record_count"],
        "pricing_tier": access["pricing_tier"],
        "products": [
            {
                "product_code": code,
                "display_name": PRODUCT_DISPLAY_NAMES.get(code, code),
                "price_eur": product_price_map.get(code, 0.0),
                "active": code in active_products,
            }
            for code in [
                PRODUCT_DATA_HEALTH_SCORE,
                PRODUCT_FULL_ANALYSIS,
                PRODUCT_VALIDATION_CHECK,
                PRODUCT_MONITORING_MONTHLY,
                PRODUCT_MONITORING_ANNUAL,
            ]
        ],
    }
