from __future__ import annotations

from sqlalchemy import select

from app.models import Tenant, TenantScanCredit
from app.services.product_license_service import (
    PRODUCT_VALIDATION_CHECK,
    build_product_access_snapshot,
)
from app.services.quick_assessment_access_service import build_quick_assessment_access_snapshot

REPORT_FREE = "free-health"
REPORT_QUICK = "quick-assessment"
REPORT_ASSESSMENT = "assessment"
REPORT_VALIDATION = "validation"


def resolve_preferred_report_variant(db, tenant: Tenant, *, scan_id: str | None = None) -> str:
    """Return the highest report variant valid for this tenant and, when supplied, scan.

    Validation is scan-specific. For ordinary scans the paid disclosure hierarchy is
    Assessment > Quick Assessment > Free Health. The decision stays server-side so
    Business Central, email delivery and future channels cannot diverge.
    """
    full_access = build_product_access_snapshot(db, tenant)

    if scan_id and full_access["validation_access_active"]:
        validation_credit = db.scalar(
            select(TenantScanCredit.id).where(
                TenantScanCredit.tenant_id == tenant.tenant_id,
                TenantScanCredit.consumed_scan_id == scan_id,
                TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
                TenantScanCredit.status == "consumed",
            )
        )
        if validation_credit is not None:
            return REPORT_VALIDATION

    if full_access["can_view_executive_report"]:
        return REPORT_ASSESSMENT

    quick_access = build_quick_assessment_access_snapshot(db, tenant)
    if quick_access["can_view_quick_assessment"]:
        return REPORT_QUICK

    return REPORT_FREE
