from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.db import SessionLocal
from app.lifecycle_models import LifecycleEmailOutbox
from app.models import Tenant, TenantProductEntitlement, TenantScanCredit
from app.operator_models import TenantOperatorAction
from app.services.lifecycle_email_service import (
    EVENT_ASSESSMENT_ACTIVATED,
    EVENT_ASSESSMENT_EXPIRING,
    EVENT_ASSESSMENT_EXPIRED,
    EVENT_ASSESSMENT_EXTENDED,
    EVENT_VALIDATION_AVAILABLE,
)
from app.services.operator_commercial_service import (
    extend_assessment,
    grant_assessment,
    grant_validation,
    revoke_product,
)
from app.services.product_license_service import (
    PRODUCT_ASSESSMENT,
    PRODUCT_VALIDATION_CHECK,
    build_product_access_snapshot,
)


def _enable_lifecycle(client, tenant, auth_header_factory, email="operator@example.com"):
    response = client.put(
        "/tenant/lifecycle-profile",
        headers=auth_header_factory(tenant),
        json={"primary_notification_email": email, "preferred_language": "en"},
    )
    assert response.status_code == 200, response.text


def _as_utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def test_assessment_unlocks_existing_scan_for_seven_days_without_scan_credit(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    _enable_lifecycle(client, tenant, auth_header_factory)
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="f4-free-baseline")

    with SessionLocal() as db:
        before_credits = db.query(TenantScanCredit).filter(
            TenantScanCredit.tenant_id == tenant["tenant_id"],
            TenantScanCredit.status == "available",
        ).count()
        result = grant_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="FIV-ASS-001",
            actor="tester",
        )
        db.commit()

        after_credits = db.query(TenantScanCredit).filter(
            TenantScanCredit.tenant_id == tenant["tenant_id"],
            TenantScanCredit.status == "available",
        ).count()
        assert after_credits == before_credits
        assert result["scan_credit_granted"] is False
        assert result["scan_id"] == "f4-free-baseline"
        assert result["report_url"] and "/reports/assessment/f4-free-baseline/" in result["report_url"]

        action = db.query(TenantOperatorAction).filter(
            TenantOperatorAction.id == result["action_id"]
        ).one()
        entitlement = db.get(TenantProductEntitlement, action.entitlement_id)
        assert entitlement is not None
        remaining = _as_utc(entitlement.valid_until_utc) - datetime.now(timezone.utc)
        assert timedelta(days=6, hours=23) < remaining <= timedelta(days=7, minutes=1)

        lifecycle_events = set(
            row.event_type for row in db.query(LifecycleEmailOutbox).filter(
                LifecycleEmailOutbox.tenant_id == tenant["tenant_id"]
            ).all()
        )
        assert EVENT_ASSESSMENT_ACTIVATED in lifecycle_events
        assert EVENT_ASSESSMENT_EXPIRING in lifecycle_events
        assert EVENT_ASSESSMENT_EXPIRED in lifecycle_events


def test_validation_rejects_free_only_scan_without_paid_assessment_baseline(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    _enable_lifecycle(client, tenant, auth_header_factory, "free-only@example.com")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="f4-free-only")

    with SessionLocal() as db:
        with pytest.raises(ValueError, match="prior paid Assessment baseline"):
            grant_validation(
                db,
                tenant_id=tenant["tenant_id"],
                sales_channel="fiverr",
                external_order_reference="FIV-VAL-FREE-ONLY",
                actor="tester",
            )
        assert db.query(TenantScanCredit).filter(
            TenantScanCredit.tenant_id == tenant["tenant_id"],
            TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
        ).count() == 0


def test_validation_grant_creates_exactly_one_credit_without_premature_access(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    _enable_lifecycle(client, tenant, auth_header_factory, "validation-operator@example.com")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="f4-assessment-baseline")

    with SessionLocal() as db:
        assessment = grant_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="FIV-ASS-BEFORE-VAL-001",
            actor="tester",
        )
        db.commit()
        assert assessment["scan_id"] == "f4-assessment-baseline"

    with SessionLocal() as db:
        result = grant_validation(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="FIV-VAL-001",
            actor="tester",
        )
        db.commit()

        credits = db.query(TenantScanCredit).filter(
            TenantScanCredit.tenant_id == tenant["tenant_id"],
            TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
        ).all()
        assert len(credits) == 1
        assert credits[0].status == "available"
        assert result["baseline_scan_id"] == "f4-assessment-baseline"
        assert result["scan_credit_granted"] is True
        assert result["access_starts_after_validation_scan"] is True

        tenant_row = db.query(Tenant).filter(Tenant.tenant_id == tenant["tenant_id"]).one()
        access_before_scan = build_product_access_snapshot(db, tenant_row)
        assert access_before_scan["validation_access_active"] is False
        assert access_before_scan["can_run_deep_scan"] is True

        validation_entitlements = db.query(TenantProductEntitlement).filter(
            TenantProductEntitlement.tenant_id == tenant["tenant_id"],
            TenantProductEntitlement.product_code == PRODUCT_VALIDATION_CHECK,
        ).all()
        assert validation_entitlements == []
        assert db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type == EVENT_VALIDATION_AVAILABLE,
        ).count() == 1

        credits[0].status = "consumed"
        credits[0].consumed_scan_id = "f4-validation-new"
        credits[0].consumed_at_utc = datetime.now(timezone.utc)
        db.flush()
        access_after_scan = build_product_access_snapshot(db, tenant_row)
        assert access_after_scan["validation_access_active"] is True


def test_same_fiverr_order_cannot_grant_assessment_twice(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    _enable_lifecycle(client, tenant, auth_header_factory)
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="f4-order-baseline")
    with SessionLocal() as db:
        grant_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="FIV-DUP-001",
            actor="tester",
        )
        db.commit()
    with SessionLocal() as db:
        with pytest.raises(ValueError, match="already used"):
            grant_assessment(
                db,
                tenant_id=tenant["tenant_id"],
                sales_channel="fiverr",
                external_order_reference="FIV-DUP-001",
                actor="tester",
            )


def test_assessment_can_be_extended_exactly_once_and_reschedules_expiry(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    _enable_lifecycle(client, tenant, auth_header_factory)
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="f4-extension-baseline")
    with SessionLocal() as db:
        granted = grant_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="FIV-ASS-EXT-BASE",
            actor="tester",
        )
        db.commit()
        original_until = _as_utc(granted["valid_until_utc"])

    with SessionLocal() as db:
        extended = extend_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="FIV-ASS-EXT-001",
            actor="tester",
        )
        db.commit()
        new_until = _as_utc(extended["valid_until_utc"])
        assert timedelta(days=6, hours=23) < (new_until - original_until) <= timedelta(days=7, minutes=1)
        assert extended["extension_number"] == 1
        assert db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type == EVENT_ASSESSMENT_EXTENDED,
        ).count() == 1

    with SessionLocal() as db:
        with pytest.raises(ValueError, match="already used"):
            extend_assessment(
                db,
                tenant_id=tenant["tenant_id"],
                sales_channel="fiverr",
                external_order_reference="FIV-ASS-EXT-002",
                actor="tester",
            )


def test_revoke_assessment_closes_access_and_suppresses_pending_lifecycle(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    _enable_lifecycle(client, tenant, auth_header_factory)
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="f4-revoke-baseline")
    with SessionLocal() as db:
        grant_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="FIV-REV-001",
            actor="tester",
        )
        db.commit()
    with SessionLocal() as db:
        result = revoke_product(
            db,
            tenant_id=tenant["tenant_id"],
            product_code=PRODUCT_ASSESSMENT,
            actor="tester",
            reason="Refunded order",
        )
        db.commit()
        assert result["entitlements_revoked"] >= 1
        tenant_row = db.query(Tenant).filter(Tenant.tenant_id == tenant["tenant_id"]).one()
        assert build_product_access_snapshot(db, tenant_row)["assessment_access_active"] is False
        pending = db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type.in_([EVENT_ASSESSMENT_EXPIRING, EVENT_ASSESSMENT_EXPIRED]),
        ).all()
        assert pending
        assert all(row.status == "suppressed" for row in pending)
