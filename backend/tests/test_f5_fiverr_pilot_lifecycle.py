from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.db import SessionLocal
from app.models import Scan, TenantProductEntitlement, TenantScanCredit
from app.services.operator_commercial_service import grant_assessment, grant_validation
from app.services.product_license_service import (
    PRODUCT_ASSESSMENT,
    PRODUCT_VALIDATION_CHECK,
    consume_scan_credit_for_scan,
)


def _headers(tenant: dict[str, str]) -> dict[str, str]:
    return {"X-Tenant-Id": tenant["tenant_id"], "X-Api-Token": tenant["api_token"]}


def test_fiverr_pilot_lifecycle_free_assessment_expiry_validation(client, scan_factory):
    registered = client.post(
        "/tenant/register",
        json={"environment_name": "BC Cloud", "app_version": "1.0.2.28-f5", "preferred_language": "de"},
    )
    assert registered.status_code == 200, registered.text
    tenant = registered.json()
    headers = _headers(tenant)

    profile = client.put(
        "/tenant/lifecycle-profile",
        headers=headers,
        json={"primary_notification_email": "pilot.lifecycle@example.com", "preferred_language": "de"},
    )
    assert profile.status_code == 200, profile.text

    initial = client.get("/license/status", headers=headers)
    assert initial.status_code == 200
    assert initial.json()["scan_credits_available"] == 1
    assert initial.json()["can_run_deep_scan"] is True
    assert initial.json()["can_view_issue_details"] is False

    free_scan_id = "F5-FREE-0001"
    started = client.post(
        "/scan/start",
        headers=headers,
        json={
            "tenant_id": tenant["tenant_id"],
            "run_id": free_scan_id,
            "scan_mode": "deep",
            "total_modules": 10,
            "company_name": "F5 Pilot GmbH",
            "environment_name": "BC Cloud",
        },
    )
    assert started.status_code == 200, started.text
    assert started.json()["credit_consumed"] is True

    scan_factory(tenant_id=tenant["tenant_id"], scan_id=free_scan_id)
    with SessionLocal() as db:
        free_scan = db.query(Scan).filter(Scan.scan_id == free_scan_id).one()
        free_scan.generated_at_utc = datetime.now(timezone.utc) - timedelta(hours=2)
        free_scan.checks_count = 199
        db.commit()

    after_free = client.get("/license/status", headers=headers)
    assert after_free.status_code == 200
    assert after_free.json()["scan_credits_available"] == 0
    assert after_free.json()["can_run_deep_scan"] is False
    assert after_free.json()["can_view_issue_details"] is False

    free_report = client.get(f"/reports/free-health/{free_scan_id}", headers=headers)
    assessment_locked = client.get(f"/reports/assessment/{free_scan_id}", headers=headers)
    assert free_report.status_code == 200, free_report.text
    assert free_report.json()["report_variant"] == "free_health"
    assert assessment_locked.status_code == 402

    with SessionLocal() as db:
        assessment = grant_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="F5-FIV-ASS-001",
            actor="f5-test",
        )
        db.commit()
        assert assessment["scan_id"] == free_scan_id
        assert assessment["scan_credit_granted"] is False

    paid_status = client.get("/license/status", headers=headers)
    assert paid_status.status_code == 200
    assert paid_status.json()["assessment_access_active"] is True
    assert paid_status.json()["scan_credits_available"] == 0
    assert paid_status.json()["can_view_issue_details"] is True

    assessment_report = client.get(f"/reports/assessment/{free_scan_id}", headers=headers)
    assert assessment_report.status_code == 200, assessment_report.text
    assert assessment_report.json()["report_variant"] == "assessment"

    with SessionLocal() as db:
        entitlement = db.query(TenantProductEntitlement).filter(
            TenantProductEntitlement.tenant_id == tenant["tenant_id"],
            TenantProductEntitlement.product_code == PRODUCT_ASSESSMENT,
            TenantProductEntitlement.status == "active",
        ).one()
        entitlement.valid_until_utc = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()

    expired_status = client.get("/license/status", headers=headers)
    assert expired_status.status_code == 200
    assert expired_status.json()["assessment_access_active"] is False
    assert expired_status.json()["can_view_issue_details"] is False
    assert client.get(f"/reports/assessment/{free_scan_id}", headers=headers).status_code == 402
    assert client.get(f"/reports/free-health/{free_scan_id}", headers=headers).status_code == 200

    with SessionLocal() as db:
        validation = grant_validation(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="F5-FIV-VAL-001",
            actor="f5-test",
        )
        db.commit()
        assert validation["baseline_scan_id"] == free_scan_id
        assert validation["scan_credit_granted"] is True
        assert validation["access_starts_after_validation_scan"] is True

    validation_available = client.get("/license/status", headers=headers)
    assert validation_available.status_code == 200
    assert validation_available.json()["validation_access_active"] is False
    assert validation_available.json()["scan_credits_available"] == 1
    assert validation_available.json()["can_run_deep_scan"] is True
    assert validation_available.json()["can_view_issue_details"] is False

    validation_scan_id = "F5-VALIDATION-0002"
    with SessionLocal() as db:
        credit = consume_scan_credit_for_scan(db, tenant_id=tenant["tenant_id"], scan_id=validation_scan_id)
        assert credit is not None
        assert credit.product_code == PRODUCT_VALIDATION_CHECK
        db.commit()

    scan_factory(tenant_id=tenant["tenant_id"], scan_id=validation_scan_id)
    with SessionLocal() as db:
        validation_scan = db.query(Scan).filter(Scan.scan_id == validation_scan_id).one()
        validation_scan.generated_at_utc = datetime.now(timezone.utc)
        validation_scan.checks_count = 199
        db.commit()

    validation_active = client.get("/license/status", headers=headers)
    assert validation_active.status_code == 200
    assert validation_active.json()["validation_access_active"] is True
    assert validation_active.json()["scan_credits_available"] == 0
    assert validation_active.json()["can_view_issue_details"] is True

    validation_report = client.get(f"/reports/validation/{validation_scan_id}", headers=headers)
    assert validation_report.status_code == 200, validation_report.text
    assert validation_report.json()["baseline_scan_id"] == free_scan_id
    assert validation_report.json()["validation_scan_id"] == validation_scan_id

    with SessionLocal() as db:
        consumed = db.query(TenantScanCredit).filter(
            TenantScanCredit.tenant_id == tenant["tenant_id"],
            TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
            TenantScanCredit.consumed_scan_id == validation_scan_id,
        ).one()
        assert consumed.status == "consumed"
        assert consumed.consumed_at_utc is not None
