from __future__ import annotations

from sqlalchemy import select

from app.models import Scan, Tenant, TenantProductEntitlement, TenantScanCredit
from app.operator_models import TenantOperatorAction
from app.services.admin_audit_service import log_admin_event
from app.services.lifecycle_email_service import (
    EVENT_QUICK_ASSESSMENT_ACTIVATED,
    queue_lifecycle_email,
    quick_assessment_report_link,
)
from app.services.operator_commercial_service import latest_scan, normalize_order_reference, normalize_sales_channel
from app.services.product_license_service import build_product_access_snapshot, grant_product_entitlement, utc_now
from app.services.quick_assessment_access_service import (
    PRODUCT_QUICK_ASSESSMENT,
    build_quick_assessment_access_snapshot,
)
from app.services.record_volume_pricing_service import fiverr_price_recommendations


def _tenant(db, tenant_id: str) -> Tenant:
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
    if tenant is None:
        raise ValueError("Tenant not found.")
    return tenant


def _assert_order_unused(db, *, channel: str, order_reference: str | None) -> None:
    if not order_reference:
        return
    existing = db.scalar(
        select(TenantOperatorAction).where(
            TenantOperatorAction.sales_channel == channel,
            TenantOperatorAction.external_order_reference == order_reference,
            TenantOperatorAction.action_type == "quick_assessment_grant",
        )
    )
    if existing is not None:
        raise ValueError(
            f"This {channel} order reference was already used for quick_assessment_grant on tenant {existing.tenant_id}."
        )


def grant_quick_assessment(
    db,
    *,
    tenant_id: str,
    sales_channel: str,
    external_order_reference: str | None,
    actor: str,
    note: str | None = None,
) -> dict:
    """Grant permanent Quick disclosure without creating or consuming scan credit.

    The entitlement may be granted before the tenant has completed its first scan.
    This supports the Fiverr flow: purchase -> register -> initial included scan ->
    Quick report is revealed automatically for that same scan.
    """
    tenant = _tenant(db, tenant_id)
    channel = normalize_sales_channel(sales_channel)
    order_ref = normalize_order_reference(external_order_reference, channel=channel)
    _assert_order_unused(db, channel=channel, order_reference=order_ref)

    scan = latest_scan(db, tenant_id)

    quick_access = build_quick_assessment_access_snapshot(db, tenant)
    if quick_access["quick_assessment_entitlement_active"]:
        raise ValueError("Quick Assessment access is already active for this tenant.")
    full_access = build_product_access_snapshot(db, tenant)
    if full_access["assessment_access_active"] or full_access["validation_access_active"] or full_access["monitoring_active"]:
        raise ValueError("A higher product tier already provides Quick Assessment access for this tenant.")

    before_credits = db.query(TenantScanCredit).filter(
        TenantScanCredit.tenant_id == tenant_id,
        TenantScanCredit.status == "available",
    ).count()
    now = utc_now()
    entitlement = grant_product_entitlement(
        db,
        tenant_id=tenant_id,
        product_code=PRODUCT_QUICK_ASSESSMENT,
        source=f"operator:{channel}",
        valid_until_utc=None,
    )

    report_url = None
    scan_id = None
    if scan is not None:
        scan_id = scan.scan_id
        report_url = quick_assessment_report_link(tenant_id=tenant_id, scan_id=scan.scan_id)

    queue_lifecycle_email(
        db,
        tenant_id=tenant_id,
        event_type=EVENT_QUICK_ASSESSMENT_ACTIVATED,
        payload={"report_url": report_url or "", "scan_id": scan_id or "", "permanent": True},
        dedupe_key=f"{EVENT_QUICK_ASSESSMENT_ACTIVATED}:entitlement:{entitlement.id}",
    )

    action = TenantOperatorAction(
        tenant_id=tenant_id,
        action_type="quick_assessment_grant",
        product_code=PRODUCT_QUICK_ASSESSMENT,
        sales_channel=channel,
        external_order_reference=order_ref,
        entitlement_id=entitlement.id,
        credit_id=None,
        related_scan_id=scan_id,
        status="completed",
        note=(note or "").strip() or None,
        actor=actor,
        created_at_utc=now,
    )
    db.add(action)
    db.flush()
    log_admin_event(
        db,
        admin_username=actor,
        action="operator.quick_assessment_grant",
        target_type="tenant",
        target_id=tenant_id,
        details={
            "product_code": PRODUCT_QUICK_ASSESSMENT,
            "sales_channel": channel,
            "external_order_reference": order_ref,
            "entitlement_id": entitlement.id,
            "credit_id": None,
            "related_scan_id": scan_id,
            "permanent": True,
        },
    )
    after_credits = db.query(TenantScanCredit).filter(
        TenantScanCredit.tenant_id == tenant_id,
        TenantScanCredit.status == "available",
    ).count()
    if after_credits != before_credits:
        raise RuntimeError("Quick Assessment must not create or consume scan credits.")

    return {
        "status": "granted",
        "action_id": action.id,
        "tenant_id": tenant.tenant_id,
        "product_code": PRODUCT_QUICK_ASSESSMENT,
        "scan_id": scan_id,
        "valid_until_utc": None,
        "report_url": report_url,
        "scan_credit_granted": False,
        "permanent": True,
    }


def revoke_quick_assessment(db, *, tenant_id: str, actor: str, reason: str) -> dict:
    _tenant(db, tenant_id)
    reason = (reason or "").strip()
    if not reason:
        raise ValueError("A revoke reason is required.")
    now = utc_now()
    rows = db.scalars(
        select(TenantProductEntitlement).where(
            TenantProductEntitlement.tenant_id == tenant_id,
            TenantProductEntitlement.product_code == PRODUCT_QUICK_ASSESSMENT,
            TenantProductEntitlement.status == "active",
        )
    ).all()
    for row in rows:
        row.status = "revoked"
        row.valid_until_utc = now
        row.updated_at_utc = now
    log_admin_event(
        db,
        admin_username=actor,
        action="operator.product_revoke",
        target_type="tenant",
        target_id=tenant_id,
        details={
            "product_code": PRODUCT_QUICK_ASSESSMENT,
            "reason": reason,
            "entitlements_revoked": len(rows),
            "credits_revoked": 0,
        },
    )
    return {
        "status": "revoked",
        "tenant_id": tenant_id,
        "product_code": PRODUCT_QUICK_ASSESSMENT,
        "entitlements_revoked": len(rows),
        "credits_revoked": 0,
    }


def operator_commercial_context(db, tenant: Tenant, scan: Scan | None = None) -> dict:
    """Return Quick access plus authoritative analyzed-volume Fiverr recommendations."""
    scan = scan or latest_scan(db, tenant.tenant_id)
    quick = build_quick_assessment_access_snapshot(db, tenant)
    context = {
        "quick_active": quick["quick_assessment_entitlement_active"],
        "quick_effective_access": quick["quick_assessment_access_active"],
        "quick_until": quick["quick_assessment_access_until"],
        "total_records": None,
        "record_class": None,
        "fiverr_pricing": None,
    }
    if scan is None:
        return context
    pricing = fiverr_price_recommendations(scan.total_records)
    context.update(
        {
            "total_records": int(scan.total_records or 0),
            "record_class": pricing["record_class"],
            "fiverr_pricing": pricing["products"],
        }
    )
    return context
