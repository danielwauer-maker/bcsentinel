from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone

import pytest

from app.db import SessionLocal
from app.models import Tenant, TenantProductEntitlement, TenantScanCredit
from app.operator_models import TenantOperatorAction
from app.routers.operator_admin import _operator_rows
from app.services.operator_quick_assessment_service import (
    grant_quick_assessment,
    revoke_quick_assessment,
)
from app.services.product_license_service import build_product_access_snapshot
from app.services.quick_assessment_access_service import (
    PRODUCT_QUICK_ASSESSMENT,
    build_quick_assessment_access_snapshot,
)


def _admin_auth_header() -> dict[str, str]:
    token = base64.b64encode(b"admin-test:admin-password-for-tests-123").decode("ascii")
    return {"Authorization": f"Basic {token}"}


def _as_utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def test_quick_grant_reuses_existing_scan_for_seven_days_without_scan_credit(
    tenant_factory, deep_scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    deep_scan_factory(tenant_id=tenant["tenant_id"], scan_id="f8e-quick-baseline", total_records=90_000)

    with SessionLocal() as db:
        before_credits = db.query(TenantScanCredit).filter(
            TenantScanCredit.tenant_id == tenant["tenant_id"],
            TenantScanCredit.status == "available",
        ).count()
        result = grant_quick_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="FIV-QUICK-001",
            actor="tester",
        )
        db.commit()

        after_credits = db.query(TenantScanCredit).filter(
            TenantScanCredit.tenant_id == tenant["tenant_id"],
            TenantScanCredit.status == "available",
        ).count()
        assert after_credits == before_credits
        assert result["scan_credit_granted"] is False
        assert result["scan_id"] == "f8e-quick-baseline"

        entitlement = db.query(TenantProductEntitlement).filter(
            TenantProductEntitlement.tenant_id == tenant["tenant_id"],
            TenantProductEntitlement.product_code == PRODUCT_QUICK_ASSESSMENT,
        ).one()
        remaining = _as_utc(entitlement.valid_until_utc) - datetime.now(timezone.utc)
        assert timedelta(days=6, hours=23) < remaining <= timedelta(days=7, minutes=1)

        action = db.query(TenantOperatorAction).filter(
            TenantOperatorAction.id == result["action_id"]
        ).one()
        assert action.action_type == "quick_assessment_grant"
        assert action.external_order_reference == "FIV-QUICK-001"
        assert action.related_scan_id == "f8e-quick-baseline"
        assert action.credit_id is None

        tenant_row = db.query(Tenant).filter(Tenant.tenant_id == tenant["tenant_id"]).one()
        quick = build_quick_assessment_access_snapshot(db, tenant_row)
        full = build_product_access_snapshot(db, tenant_row)
        assert quick["quick_assessment_entitlement_active"] is True
        assert quick["can_view_quick_findings"] is True
        assert full["assessment_access_active"] is False
        assert full["validation_access_active"] is False
        assert full["can_view_issue_details"] is False
        assert full["can_view_executive_report"] is False


def test_quick_requires_existing_scan_and_unique_fiverr_order(tenant_factory, deep_scan_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    with SessionLocal() as db:
        with pytest.raises(ValueError, match="existing completed Data Health Scan"):
            grant_quick_assessment(
                db,
                tenant_id=tenant["tenant_id"],
                sales_channel="fiverr",
                external_order_reference="FIV-QUICK-NO-SCAN",
                actor="tester",
            )

    deep_scan_factory(tenant_id=tenant["tenant_id"], scan_id="f8e-order-scan", total_records=120_000)
    with SessionLocal() as db:
        grant_quick_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="FIV-QUICK-DUP",
            actor="tester",
        )
        db.commit()
    with SessionLocal() as db:
        with pytest.raises(ValueError, match="already used"):
            grant_quick_assessment(
                db,
                tenant_id=tenant["tenant_id"],
                sales_channel="fiverr",
                external_order_reference="FIV-QUICK-DUP",
                actor="tester",
            )


def test_operator_rows_use_authoritative_scan_volume_for_fiverr_recommendations(
    tenant_factory, deep_scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active", tenant_id="ten_f8e_pricing")
    deep_scan_factory(tenant_id=tenant["tenant_id"], scan_id="f8e-pricing-scan", total_records=250_001)
    with SessionLocal() as db:
        row = next(row for row in _operator_rows(db, "ten_f8e_pricing") if row["tenant_id"] == tenant["tenant_id"])
        assert row["total_records"] == 250_001
        assert row["record_class"]["code"] == "medium"
        assert row["fiverr_pricing"]["quick_assessment"]["price"] == 229.0
        assert row["fiverr_pricing"]["assessment"]["price"] == 449.0
        assert row["fiverr_pricing"]["validation_check"]["price"] == 229.0


def test_operator_rows_do_not_guess_pricing_without_scan(tenant_factory):
    tenant = tenant_factory(plan="free", license_status="active", tenant_id="ten_f8e_noscan")
    with SessionLocal() as db:
        row = next(row for row in _operator_rows(db, "ten_f8e_noscan") if row["tenant_id"] == tenant["tenant_id"])
        assert row["total_records"] is None
        assert row["record_class"] is None
        assert row["fiverr_pricing"] is None


def test_quick_revoke_removes_only_quick_entitlement(tenant_factory, deep_scan_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    deep_scan_factory(tenant_id=tenant["tenant_id"], scan_id="f8e-revoke-scan", total_records=100_000)
    with SessionLocal() as db:
        grant_quick_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="FIV-QUICK-REV",
            actor="tester",
        )
        db.commit()
    with SessionLocal() as db:
        result = revoke_quick_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            actor="tester",
            reason="Refunded order",
        )
        db.commit()
        assert result["entitlements_revoked"] == 1
        tenant_row = db.query(Tenant).filter(Tenant.tenant_id == tenant["tenant_id"]).one()
        quick = build_quick_assessment_access_snapshot(db, tenant_row)
        assert quick["quick_assessment_entitlement_active"] is False
        assert quick["can_view_quick_assessment"] is False


def test_operator_console_renders_quick_action_and_authoritative_pricing(
    client, tenant_factory, deep_scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active", tenant_id="ten_f8e_console")
    deep_scan_factory(tenant_id=tenant["tenant_id"], scan_id="f8e-console-scan", total_records=1_000_001)
    response = client.get("/admin/operator?q=ten_f8e_console", headers=_admin_auth_header())
    assert response.status_code == 200
    assert "Grant Quick Assessment" in response.text
    assert "1.000.001" in response.text
    assert "Large class" in response.text
    assert "$349" in response.text
    assert "$649" in response.text
    assert "$329" in response.text
