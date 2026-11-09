from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib

from sqlalchemy import select

from app.lifecycle_models import LifecycleEmailOutbox
from app.models import Scan, Subscription, Tenant, TenantProductEntitlement, TenantProductPurchase, TenantScanCredit
from app.operator_models import TenantOperatorAction
from app.services.admin_audit_service import log_admin_event
from app.services.lifecycle_email_service import (
    EVENT_ASSESSMENT_ACTIVATED,
    EVENT_ASSESSMENT_EXPIRING,
    EVENT_ASSESSMENT_EXPIRED,
    EVENT_ASSESSMENT_EXTENDED,
    EVENT_VALIDATION_AVAILABLE,
    queue_lifecycle_email,
    report_link,
    schedule_entitlement_lifecycle,
)
from app.services.product_license_service import (
    PRODUCT_ASSESSMENT,
    PRODUCT_VALIDATION_CHECK,
    grant_product_entitlement,
    grant_scan_credit,
    utc_now,
)

ALLOWED_SALES_CHANNELS = {
    "fiverr",
    "direct",
    "malt",
    "contra",
    "appsource",
    "partner",
    "support",
}
ASSESSMENT_DAYS = 7
ASSESSMENT_EXTENSION_DAYS = 7


def _fiverr_position_key(order_reference: str, order_position: str) -> str:
    order = (order_reference or "").strip()
    position = (order_position or "").strip()
    if not order or not position or len(order) > 120 or len(position) > 120:
        raise ValueError("A Fiverr order and position are required.")
    digest = hashlib.sha256((str(len(order)) + ":" + order + position).encode("utf-8")).hexdigest()
    return "fiverr:" + digest


def grant_fiverr_v2(db, *, tenant_id: str, product_code: str, order_reference: str,
                    order_position: str, amount: float, actor: str) -> TenantOperatorAction:
    """Record an operator-confirmed Fiverr payment and apply the v2 purchase grant."""
    from app.assessment_scope_models import AssessmentScopeSnapshot
    from app.core.settings import settings
    from app.services.product_license_service import (
        NEW_ACCESS_PRODUCTS, PRODUCT_FULL_ASSESSMENT_V2, grant_v2_access_purchase,
        is_original_free_scan, record_product_purchase,
    )
    from app.services.scan_company_service import canonical_company_id
    from app.services.tenant_access_service import enforce_tenant_is_active

    if not settings.ACCESS_MODEL_V2_ENABLED or product_code not in NEW_ACCESS_PRODUCTS:
        raise ValueError("V2 product is unavailable.")
    if not actor or not (0 < amount < 100000000):
        raise ValueError("A confirmed positive EUR payment and operator are required.")
    key = _fiverr_position_key(order_reference, order_position)
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id).with_for_update())
    if tenant is None:
        raise ValueError("Tenant not found.")
    enforce_tenant_is_active(db, tenant_id)
    if db.scalar(select(TenantOperatorAction.id).where(
        TenantOperatorAction.sales_channel == "fiverr", TenantOperatorAction.external_order_reference == key,
        TenantOperatorAction.action_type == "v2_purchase_revoke",
    ).limit(1)) is not None:
        raise ValueError("Order position has already been reversed.")
    purchase = db.scalar(select(TenantProductPurchase).where(
        TenantProductPurchase.provider_checkout_session_id == key,
    ))
    if purchase is not None:
        if (purchase.provider != "fiverr" or purchase.tenant_id != tenant_id
                or purchase.product_code != product_code or purchase.status != "paid"
                or purchase.amount_total != amount):
            raise ValueError("Order position conflicts with an existing purchase.")
        previous = db.scalar(select(TenantOperatorAction).where(
            TenantOperatorAction.sales_channel == "fiverr",
            TenantOperatorAction.external_order_reference == key,
            TenantOperatorAction.action_type == "v2_purchase_grant",
        ))
        if previous is None:
            raise ValueError("Order position has no completed operator grant.")
        return previous

    baseline = None
    for scan in db.scalars(select(Scan).where(Scan.tenant_id == tenant_id)).all():
        if not is_original_free_scan(db, tenant_id, scan.scan_id):
            continue
        try:
            company_matches = canonical_company_id(scan.bc_company_id) == canonical_company_id(tenant.bc_company_id)
        except ValueError:
            company_matches = False
        scope = db.scalar(select(AssessmentScopeSnapshot).where(
            AssessmentScopeSnapshot.scan_id == scan.scan_id,
            AssessmentScopeSnapshot.tenant_id == tenant_id,
            AssessmentScopeSnapshot.state == "confirmed",
            AssessmentScopeSnapshot.confirmed_at_utc.is_not(None),
            AssessmentScopeSnapshot.included_modules_count > 0,
        ).order_by(AssessmentScopeSnapshot.version.desc()))
        if company_matches and str(scan.lcy_code or "").upper() == "EUR" and scope is not None:
            baseline = scan
            break
    if baseline is None:
        raise ValueError("A verified original Free scan with confirmed company, EUR and scope is required.")
    if product_code != PRODUCT_FULL_ASSESSMENT_V2:
        full = db.scalar(select(TenantProductPurchase.id).where(
            TenantProductPurchase.tenant_id == tenant_id,
            TenantProductPurchase.product_code == PRODUCT_FULL_ASSESSMENT_V2,
            TenantProductPurchase.status.in_(["paid", "complete", "completed"]),
        ).limit(1))
        if full is None:
            raise ValueError("A verified Full Assessment baseline is required.")
    purchase = record_product_purchase(
        db, tenant_id=tenant_id, product_code=product_code, provider="fiverr",
        provider_checkout_session_id=key, provider_payment_intent_id=None,
        status="paid", currency="EUR", amount_total=amount, source="operator",
    )
    entitlement = grant_v2_access_purchase(db, tenant_id=tenant_id, product_code=product_code, purchase_id=purchase.id)
    credit = db.scalar(select(TenantScanCredit).where(TenantScanCredit.source_purchase_id == purchase.id))
    return _record_action(
        db, tenant_id=tenant_id, action_type="v2_purchase_grant", product_code=product_code,
        channel="fiverr", order_reference=key, actor=actor, entitlement_id=entitlement.id,
        credit_id=credit.id if credit else None, related_scan_id=baseline.scan_id,
        note=f"Fiverr order {order_reference.strip()}, position {order_position.strip()}",
    )


def revoke_fiverr_v2(db, *, tenant_id: str, order_reference: str, order_position: str, actor: str,
                     reason: str = "confirmed refund") -> TenantOperatorAction:
    from app.services.product_license_service import reverse_v2_purchase

    if not actor or not (reason or "").strip():
        raise ValueError("An operator and refund reason are required.")
    key = _fiverr_position_key(order_reference, order_position)
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id).with_for_update())
    if tenant is None:
        raise ValueError("Tenant not found.")
    purchase = db.scalar(select(TenantProductPurchase).where(
        TenantProductPurchase.tenant_id == tenant_id,
        TenantProductPurchase.provider == "fiverr",
        TenantProductPurchase.provider_checkout_session_id == key,
    ))
    prior = db.scalar(select(TenantOperatorAction).where(
        TenantOperatorAction.sales_channel == "fiverr", TenantOperatorAction.external_order_reference == key,
        TenantOperatorAction.action_type == "v2_purchase_revoke",
    ))
    if prior is not None:
        if prior.tenant_id != tenant_id:
            raise ValueError("Order position belongs to another tenant.")
        return prior
    if purchase is None:
        if db.scalar(select(TenantProductPurchase.id).where(
            TenantProductPurchase.provider_checkout_session_id == key,
        ).limit(1)) is not None:
            raise ValueError("Order position belongs to another tenant.")
        now = utc_now()
        db.add(TenantProductPurchase(
            tenant_id=tenant_id, product_code="unknown", provider="fiverr",
            provider_checkout_session_id=key, status="refunded", currency="EUR",
            amount_total=0, source="operator", created_at_utc=now, updated_at_utc=now,
        ))
        db.flush()
        return _record_action(db, tenant_id=tenant_id, action_type="v2_purchase_revoke", product_code="unknown",
                              channel="fiverr", order_reference=key, actor=actor, note=reason)
    from app.services.product_license_service import MONITORING_PRODUCTS
    if purchase.product_code in MONITORING_PRODUCTS:
        subscription = db.scalar(select(Subscription).where(
            Subscription.tenant_id == tenant_id, Subscription.provider == "fiverr",
            Subscription.provider_subscription_id == key,
        ).with_for_update())
        if subscription is None:
            raise ValueError("Monitoring subscription not found.")
        subscription.status = "canceled"
        subscription.updated_at_utc = utc_now()
        purchase.status = "refunded"
        purchase.updated_at_utc = utc_now()
    else:
        reverse_v2_purchase(db, purchase_id=purchase.id, tenant_id=tenant_id, event_type="charge.refunded")
    return _record_action(db, tenant_id=tenant_id, action_type="v2_purchase_revoke", product_code=purchase.product_code,
                          channel="fiverr", order_reference=key, actor=actor, note=reason)


def grant_fiverr_monitoring(db, *, tenant_id: str, product_code: str, order_reference: str,
                            order_position: str, amount: float, period_start: datetime,
                            period_end: datetime, actor: str) -> TenantOperatorAction:
    from app.core.settings import settings
    from app.services.product_license_service import MONITORING_PRODUCTS, PRODUCT_MONITORING_MONTHLY, record_product_purchase
    from app.services.tenant_access_service import enforce_tenant_is_active

    if not settings.ACCESS_MODEL_V2_ENABLED or product_code not in MONITORING_PRODUCTS:
        raise ValueError("Monitoring product is unavailable.")
    if not actor or not (0 < amount < 100000000):
        raise ValueError("A confirmed positive EUR payment and operator are required.")
    if period_start.tzinfo is None or period_end.tzinfo is None or period_end <= period_start:
        raise ValueError("Valid timezone-aware subscription dates are required.")
    key = _fiverr_position_key(order_reference, order_position)
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id).with_for_update())
    if tenant is None:
        raise ValueError("Tenant not found.")
    enforce_tenant_is_active(db, tenant_id)
    if db.scalar(select(TenantOperatorAction.id).where(
        TenantOperatorAction.sales_channel == "fiverr", TenantOperatorAction.external_order_reference == key,
        TenantOperatorAction.action_type == "v2_purchase_revoke",
    ).limit(1)) is not None:
        raise ValueError("Order position has already been reversed.")
    purchase = db.scalar(select(TenantProductPurchase).where(TenantProductPurchase.provider_checkout_session_id == key))
    if purchase is not None:
        subscription = db.scalar(select(Subscription).where(Subscription.provider_subscription_id == key))
        action = db.scalar(select(TenantOperatorAction).where(
            TenantOperatorAction.sales_channel == "fiverr", TenantOperatorAction.external_order_reference == key,
            TenantOperatorAction.action_type == "v2_purchase_grant",
        ))
        if (purchase.tenant_id != tenant_id or purchase.product_code != product_code or purchase.status != "paid"
                or purchase.amount_total != amount or subscription is None or action is None
                or _as_utc(subscription.current_period_start_utc) != _as_utc(period_start)
                or _as_utc(subscription.current_period_end_utc) != _as_utc(period_end)):
            raise ValueError("Order position conflicts with an existing purchase.")
        return action
    record_product_purchase(db, tenant_id=tenant_id, product_code=product_code, provider="fiverr",
                            provider_checkout_session_id=key, provider_payment_intent_id=None,
                            status="paid", currency="EUR", amount_total=amount, source="operator")
    now = utc_now()
    db.add(Subscription(tenant_id=tenant_id, provider="fiverr", provider_subscription_id=key,
                        status="active", plan_code=product_code, currency="EUR",
                        amount_monthly=amount if product_code == PRODUCT_MONITORING_MONTHLY else 0,
                        current_period_start_utc=period_start, current_period_end_utc=period_end,
                        created_at_utc=now, updated_at_utc=now))
    db.flush()
    return _record_action(db, tenant_id=tenant_id, action_type="v2_purchase_grant", product_code=product_code,
                          channel="fiverr", order_reference=key, actor=actor,
                          note=f"Fiverr order {order_reference.strip()}, position {order_position.strip()}")


def cancel_fiverr_monitoring(db, *, tenant_id: str, order_reference: str, order_position: str, actor: str) -> TenantOperatorAction:
    key = _fiverr_position_key(order_reference, order_position)
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id).with_for_update())
    if tenant is None:
        raise ValueError("Tenant not found.")
    subscription = db.scalar(select(Subscription).where(
        Subscription.tenant_id == tenant_id, Subscription.provider == "fiverr",
        Subscription.provider_subscription_id == key,
    ).with_for_update())
    if subscription is None or subscription.status not in {"active", "trialing"}:
        raise ValueError("Active monitoring subscription not found.")
    prior = db.scalar(select(TenantOperatorAction).where(
        TenantOperatorAction.sales_channel == "fiverr", TenantOperatorAction.external_order_reference == key,
        TenantOperatorAction.action_type == "v2_monitoring_cancel",
    ))
    if prior is not None:
        return prior
    subscription.cancel_at_period_end = True
    subscription.updated_at_utc = utc_now()
    return _record_action(db, tenant_id=tenant_id, action_type="v2_monitoring_cancel", product_code=subscription.plan_code,
                          channel="fiverr", order_reference=key, actor=actor)


def normalize_sales_channel(value: str | None) -> str:
    channel = (value or "direct").strip().lower()
    if channel not in ALLOWED_SALES_CHANNELS:
        raise ValueError(f"Unsupported sales channel: {channel}")
    return channel


def normalize_order_reference(value: str | None, *, channel: str) -> str | None:
    ref = (value or "").strip()
    if channel == "fiverr" and not ref:
        raise ValueError("A Fiverr Order ID/reference is required.")
    if len(ref) > 120:
        raise ValueError("External order reference is too long.")
    return ref or None


def _as_utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _tenant(db, tenant_id: str) -> Tenant:
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
    if tenant is None:
        raise ValueError("Tenant not found.")
    return tenant


def latest_scan(db, tenant_id: str) -> Scan | None:
    return db.scalar(
        select(Scan)
        .where(Scan.tenant_id == tenant_id)
        .order_by(Scan.generated_at_utc.desc(), Scan.id.desc())
        .limit(1)
    )


def _assessment_baseline_scan(db, tenant_id: str) -> Scan | None:
    """Resolve a Validation baseline only after a real paid Assessment exists.

    Operator-granted Assessments retain the exact scan they unlocked. For direct
    checkout / legacy paid flows without an operator action, an Assessment
    entitlement or completed Assessment purchase is accepted as paid proof and
    the latest tenant scan becomes the baseline.
    """
    action = db.scalar(
        select(TenantOperatorAction)
        .where(
            TenantOperatorAction.tenant_id == tenant_id,
            TenantOperatorAction.action_type == "assessment_grant",
            TenantOperatorAction.status == "completed",
            TenantOperatorAction.related_scan_id.is_not(None),
        )
        .order_by(TenantOperatorAction.created_at_utc.desc(), TenantOperatorAction.id.desc())
        .limit(1)
    )
    if action is not None and action.related_scan_id:
        scan = db.scalar(
            select(Scan).where(
                Scan.tenant_id == tenant_id,
                Scan.scan_id == action.related_scan_id,
            )
        )
        if scan is not None:
            return scan

    entitlement = db.scalar(
        select(TenantProductEntitlement)
        .where(
            TenantProductEntitlement.tenant_id == tenant_id,
            TenantProductEntitlement.product_code == PRODUCT_ASSESSMENT,
        )
        .order_by(TenantProductEntitlement.created_at_utc.desc(), TenantProductEntitlement.id.desc())
        .limit(1)
    )
    purchase = db.scalar(
        select(TenantProductPurchase)
        .where(
            TenantProductPurchase.tenant_id == tenant_id,
            TenantProductPurchase.product_code == PRODUCT_ASSESSMENT,
            TenantProductPurchase.status.in_(["paid", "complete", "completed"]),
        )
        .order_by(TenantProductPurchase.created_at_utc.desc(), TenantProductPurchase.id.desc())
        .limit(1)
    )
    if entitlement is None and purchase is None:
        return None
    return latest_scan(db, tenant_id)


def _assert_order_unused(db, *, channel: str, order_reference: str | None, action_type: str) -> None:
    if not order_reference:
        return
    existing = db.scalar(
        select(TenantOperatorAction).where(
            TenantOperatorAction.sales_channel == channel,
            TenantOperatorAction.external_order_reference == order_reference,
            TenantOperatorAction.action_type == action_type,
        )
    )
    if existing is not None:
        raise ValueError(
            f"This {channel} order reference was already used for {action_type} on tenant {existing.tenant_id}."
        )


def _record_action(
    db,
    *,
    tenant_id: str,
    action_type: str,
    product_code: str,
    channel: str,
    order_reference: str | None,
    actor: str,
    entitlement_id: int | None = None,
    credit_id: int | None = None,
    related_scan_id: str | None = None,
    note: str | None = None,
) -> TenantOperatorAction:
    action = TenantOperatorAction(
        tenant_id=tenant_id,
        action_type=action_type,
        product_code=product_code,
        sales_channel=channel,
        external_order_reference=order_reference,
        entitlement_id=entitlement_id,
        credit_id=credit_id,
        related_scan_id=related_scan_id,
        status="completed",
        note=(note or "").strip() or None,
        actor=actor,
        created_at_utc=utc_now(),
    )
    db.add(action)
    db.flush()
    log_admin_event(
        db,
        admin_username=actor,
        action=f"operator.{action_type}",
        target_type="tenant",
        target_id=tenant_id,
        details={
            "product_code": product_code,
            "sales_channel": channel,
            "external_order_reference": order_reference,
            "entitlement_id": entitlement_id,
            "credit_id": credit_id,
            "related_scan_id": related_scan_id,
        },
    )
    return action


def grant_assessment(
    db,
    *,
    tenant_id: str,
    sales_channel: str,
    external_order_reference: str | None,
    actor: str,
    note: str | None = None,
) -> dict:
    tenant = _tenant(db, tenant_id)
    channel = normalize_sales_channel(sales_channel)
    order_ref = normalize_order_reference(external_order_reference, channel=channel)
    _assert_order_unused(db, channel=channel, order_reference=order_ref, action_type="assessment_grant")

    scan = latest_scan(db, tenant_id)
    if scan is None:
        raise ValueError("Assessment requires an existing completed Data Health Scan. Run the initial Free scan first.")

    now = utc_now()
    active = db.scalar(
        select(TenantProductEntitlement).where(
            TenantProductEntitlement.tenant_id == tenant_id,
            TenantProductEntitlement.product_code == PRODUCT_ASSESSMENT,
            TenantProductEntitlement.status == "active",
            TenantProductEntitlement.valid_until_utc >= now,
        ).order_by(TenantProductEntitlement.valid_until_utc.desc())
    )
    if active is not None:
        raise ValueError("Assessment access is already active. Use Extend Assessment instead of granting a second Assessment.")

    entitlement = grant_product_entitlement(
        db,
        tenant_id=tenant_id,
        product_code=PRODUCT_ASSESSMENT,
        source=f"operator:{channel}",
        valid_until_utc=now + timedelta(days=ASSESSMENT_DAYS),
    )
    link = report_link(db, tenant_id=tenant_id, scan_id=scan.scan_id)
    schedule_entitlement_lifecycle(
        db,
        tenant_id=tenant_id,
        entitlement=entitlement,
        activation_event=EVENT_ASSESSMENT_ACTIVATED,
        payload={"report_url": link or "", "scan_id": scan.scan_id},
    )
    action = _record_action(
        db,
        tenant_id=tenant_id,
        action_type="assessment_grant",
        product_code=PRODUCT_ASSESSMENT,
        channel=channel,
        order_reference=order_ref,
        actor=actor,
        entitlement_id=entitlement.id,
        related_scan_id=scan.scan_id,
        note=note,
    )
    return {
        "status": "granted",
        "action_id": action.id,
        "tenant_id": tenant.tenant_id,
        "product_code": PRODUCT_ASSESSMENT,
        "scan_id": scan.scan_id,
        "valid_until_utc": entitlement.valid_until_utc,
        "report_url": link,
        "scan_credit_granted": False,
    }


def grant_validation(
    db,
    *,
    tenant_id: str,
    sales_channel: str,
    external_order_reference: str | None,
    actor: str,
    note: str | None = None,
) -> dict:
    tenant = _tenant(db, tenant_id)
    channel = normalize_sales_channel(sales_channel)
    order_ref = normalize_order_reference(external_order_reference, channel=channel)
    _assert_order_unused(db, channel=channel, order_reference=order_ref, action_type="validation_grant")

    baseline = _assessment_baseline_scan(db, tenant_id)
    if baseline is None:
        raise ValueError("Validation requires a prior paid Assessment baseline.")

    existing_credit = db.scalar(
        select(TenantScanCredit).where(
            TenantScanCredit.tenant_id == tenant_id,
            TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
            TenantScanCredit.status == "available",
        )
    )
    if existing_credit is not None:
        raise ValueError("A Validation scan is already available for this tenant.")

    credit = grant_scan_credit(
        db,
        tenant_id=tenant_id,
        product_code=PRODUCT_VALIDATION_CHECK,
        source=f"operator:{channel}",
    )
    queue_lifecycle_email(
        db,
        tenant_id=tenant_id,
        event_type=EVENT_VALIDATION_AVAILABLE,
        payload={"baseline_scan_id": baseline.scan_id},
        dedupe_key=f"{EVENT_VALIDATION_AVAILABLE}:credit:{credit.id}",
    )
    action = _record_action(
        db,
        tenant_id=tenant_id,
        action_type="validation_grant",
        product_code=PRODUCT_VALIDATION_CHECK,
        channel=channel,
        order_reference=order_ref,
        actor=actor,
        credit_id=credit.id,
        related_scan_id=baseline.scan_id,
        note=note,
    )
    return {
        "status": "granted",
        "action_id": action.id,
        "tenant_id": tenant.tenant_id,
        "product_code": PRODUCT_VALIDATION_CHECK,
        "baseline_scan_id": baseline.scan_id,
        "credit_id": credit.id,
        "scan_credit_granted": True,
        "access_starts_after_validation_scan": True,
    }


def _latest_assessment_entitlement(db, tenant_id: str) -> TenantProductEntitlement | None:
    return db.scalar(
        select(TenantProductEntitlement)
        .where(
            TenantProductEntitlement.tenant_id == tenant_id,
            TenantProductEntitlement.product_code == PRODUCT_ASSESSMENT,
        )
        .order_by(TenantProductEntitlement.created_at_utc.desc(), TenantProductEntitlement.id.desc())
        .limit(1)
    )


def extend_assessment(
    db,
    *,
    tenant_id: str,
    sales_channel: str,
    external_order_reference: str | None,
    actor: str,
    note: str | None = None,
) -> dict:
    _tenant(db, tenant_id)
    channel = normalize_sales_channel(sales_channel)
    order_ref = normalize_order_reference(external_order_reference, channel=channel)
    _assert_order_unused(db, channel=channel, order_reference=order_ref, action_type="assessment_extend")

    entitlement = _latest_assessment_entitlement(db, tenant_id)
    if entitlement is None:
        raise ValueError("No Assessment entitlement exists to extend.")
    previous_extension = db.scalar(
        select(TenantOperatorAction).where(
            TenantOperatorAction.tenant_id == tenant_id,
            TenantOperatorAction.action_type == "assessment_extend",
            TenantOperatorAction.entitlement_id == entitlement.id,
            TenantOperatorAction.status == "completed",
        )
    )
    if previous_extension is not None:
        raise ValueError("This Assessment has already used its one allowed 7-day extension.")

    now = utc_now()
    current_until = _as_utc(entitlement.valid_until_utc) or now
    new_until = max(current_until, now) + timedelta(days=ASSESSMENT_EXTENSION_DAYS)
    entitlement.status = "active"
    entitlement.valid_until_utc = new_until
    entitlement.updated_at_utc = now

    scan = latest_scan(db, tenant_id)
    scan_id = scan.scan_id if scan is not None else None
    link = report_link(db, tenant_id=tenant_id, scan_id=scan_id) if scan_id else None
    for event_type in (EVENT_ASSESSMENT_EXPIRING, EVENT_ASSESSMENT_EXPIRED):
        old = db.scalar(
            select(LifecycleEmailOutbox).where(
                LifecycleEmailOutbox.dedupe_key == f"{event_type}:entitlement:{entitlement.id}"
            )
        )
        if old is not None and old.status in {"queued", "failed"}:
            old.status = "suppressed"
            old.updated_at_utc = now

    payload = {
        "valid_until_utc": new_until.isoformat().replace("+00:00", "Z"),
        "report_url": link or "",
        "scan_id": scan_id or "",
    }
    queue_lifecycle_email(
        db,
        tenant_id=tenant_id,
        event_type=EVENT_ASSESSMENT_EXTENDED,
        payload=payload,
        dedupe_key=f"{EVENT_ASSESSMENT_EXTENDED}:entitlement:{entitlement.id}:extension:1",
    )
    queue_lifecycle_email(
        db,
        tenant_id=tenant_id,
        event_type=EVENT_ASSESSMENT_EXPIRING,
        payload=payload,
        dedupe_key=f"{EVENT_ASSESSMENT_EXPIRING}:entitlement:{entitlement.id}:extension:1",
        scheduled_at_utc=new_until - timedelta(hours=48),
    )
    queue_lifecycle_email(
        db,
        tenant_id=tenant_id,
        event_type=EVENT_ASSESSMENT_EXPIRED,
        payload=payload,
        dedupe_key=f"{EVENT_ASSESSMENT_EXPIRED}:entitlement:{entitlement.id}:extension:1",
        scheduled_at_utc=new_until,
    )
    action = _record_action(
        db,
        tenant_id=tenant_id,
        action_type="assessment_extend",
        product_code=PRODUCT_ASSESSMENT,
        channel=channel,
        order_reference=order_ref,
        actor=actor,
        entitlement_id=entitlement.id,
        related_scan_id=scan_id,
        note=note,
    )
    return {
        "status": "extended",
        "action_id": action.id,
        "tenant_id": tenant_id,
        "product_code": PRODUCT_ASSESSMENT,
        "valid_until_utc": new_until,
        "extension_days": ASSESSMENT_EXTENSION_DAYS,
        "extension_number": 1,
        "report_url": link,
    }


def revoke_product(
    db,
    *,
    tenant_id: str,
    product_code: str,
    actor: str,
    reason: str,
) -> dict:
    _tenant(db, tenant_id)
    product = (product_code or "").strip().lower()
    if product not in {PRODUCT_ASSESSMENT, PRODUCT_VALIDATION_CHECK}:
        raise ValueError("Operator revoke supports Assessment or Validation only.")
    now = utc_now()
    changed_entitlements = 0
    changed_credits = 0
    entitlements = db.scalars(
        select(TenantProductEntitlement).where(
            TenantProductEntitlement.tenant_id == tenant_id,
            TenantProductEntitlement.product_code == product,
            TenantProductEntitlement.status == "active",
        )
    ).all()
    for entitlement in entitlements:
        entitlement.status = "revoked"
        entitlement.valid_until_utc = now - timedelta(seconds=1)
        entitlement.updated_at_utc = now
        changed_entitlements += 1
    credits = db.scalars(
        select(TenantScanCredit).where(
            TenantScanCredit.tenant_id == tenant_id,
            TenantScanCredit.product_code == product,
            TenantScanCredit.status == "available",
        )
    ).all()
    for credit in credits:
        credit.status = "revoked"
        changed_credits += 1
    pending = db.scalars(
        select(LifecycleEmailOutbox).where(
            LifecycleEmailOutbox.tenant_id == tenant_id,
            LifecycleEmailOutbox.status.in_(["queued", "failed"]),
        )
    ).all()
    for row in pending:
        if (product == PRODUCT_ASSESSMENT and row.event_type.startswith("assessment.")) or (
            product == PRODUCT_VALIDATION_CHECK and row.event_type.startswith("validation.")
        ):
            row.status = "suppressed"
            row.updated_at_utc = now
    action = _record_action(
        db,
        tenant_id=tenant_id,
        action_type="product_revoke",
        product_code=product,
        channel="support",
        order_reference=None,
        actor=actor,
        note=reason,
    )
    return {
        "status": "revoked",
        "action_id": action.id,
        "tenant_id": tenant_id,
        "product_code": product,
        "entitlements_revoked": changed_entitlements,
        "credits_revoked": changed_credits,
    }
