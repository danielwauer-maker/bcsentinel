"""Versioned BCSentinel product rules for the Free / Full / Renewal / Monitoring model.

This module intentionally has no database side effects. It is a policy foundation;
existing billing, API handlers and tenant records MUST be migrated and wired separately.
Never use a client-provided tier as proof of entitlement.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


ACCESS_DAYS = 14


class Product(str, Enum):
    FREE = "free"
    FULL_ASSESSMENT = "full_assessment"
    ACCESS_RENEWAL = "access_renewal"
    ACCESS_RENEWAL_VALIDATION = "access_renewal_validation"
    MONITORING = "monitoring"


@dataclass(frozen=True)
class Grant:
    product: Product
    premium_days: int
    additional_scans: int | None  # None: monitoring scans, subject to fair-use controls.
    free_report_permanent: bool


GRANTS: dict[Product, Grant] = {
    Product.FREE: Grant(Product.FREE, 0, 1, True),
    Product.FULL_ASSESSMENT: Grant(Product.FULL_ASSESSMENT, ACCESS_DAYS, 0, False),
    Product.ACCESS_RENEWAL: Grant(Product.ACCESS_RENEWAL, ACCESS_DAYS, 0, False),
    Product.ACCESS_RENEWAL_VALIDATION: Grant(Product.ACCESS_RENEWAL_VALIDATION, ACCESS_DAYS, 1, False),
    Product.MONITORING: Grant(Product.MONITORING, 0, None, False),
}


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("Naive timestamps are not permitted for access grants")
    return value.astimezone(timezone.utc)


def extend_access(
    existing_until: datetime | None,
    activated_at: datetime,
    *,
    duration_days: int = ACCESS_DAYS,
) -> datetime:
    """Append 14 days to remaining paid time, otherwise start from activation."""
    if duration_days <= 0:
        raise ValueError("Access duration must be positive")
    start = as_utc(activated_at)
    if existing_until is not None:
        current_end = as_utc(existing_until)
        if current_end > start:
            start = current_end
    return start + timedelta(days=duration_days)


def report_visible(
    *,
    report_type: str,
    premium_active: bool,
    monitoring_active: bool,
    is_original_free_report: bool,
) -> bool:
    """Only the original Free report survives premium expiry.

    This policy grants no tenancy/company authorization and must be combined with
    server-side authenticated tenant, company and scan ownership checks.
    """
    if report_type == "free":
        return is_original_free_report
    if report_type in {"full", "validation"}:
        return premium_active or monitoring_active
    if report_type == "monitoring":
        return monitoring_active
    return False


def new_manual_scan_allowed(
    *,
    free_scan_unused: bool,
    validation_credits_available: int,
    monitoring_active: bool,
) -> bool:
    """Full Assessment and scan-less Renewal alone never grant extra scans."""
    return monitoring_active or free_scan_unused or validation_credits_available > 0
