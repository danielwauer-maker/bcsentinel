from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.db import SessionLocal
from app.models import Scan, TenantProductEntitlement, TenantScanCredit
from app.services.operator_commercial_service import grant_assessment, grant_validation
from app.services.operator_quick_assessment_service import grant_quick_assessment
from app.services.product_license_service import PRODUCT_ASSESSMENT, PRODUCT_VALIDATION_CHECK
from app.services.quick_assessment_access_service import PRODUCT_QUICK_ASSESSMENT


def _headers(tenant: dict[str, str]) -> dict[str, str]:
    return {"X-Tenant-Id": tenant["tenant_id"], "X-Api-Token": tenant["api_token"]}


def _complete_scan(scan_id: str, *, score: int, total_records: int, generated_at: datetime) -> None:
    with SessionLocal() as db:
        scan = db.query(Scan).filter(Scan.scan_id == scan_id).one()
        scan.generated_at_utc = generated_at
        scan.data_score = score
        scan.checks_count = 199
        scan.issues_count = 0
        scan.total_records = total_records
        scan.summary_headline = "BCSentinel Data Health Scan completed"
        scan.summary_rating = "Good"
        for field in ("system_score", "finance_score", "sales_score", "purchasing_score", "inventory_score", "crm_score", "manufacturing_score", "service_score", "jobs_score", "hr_score"):
            setattr(scan, field, score)
        db.commit()


def _expire_entitlement(tenant_id: str, product_code: str) -> None:
    with SessionLocal() as db:
        entitlement = (
            db.query(TenantProductEntitlement)
            .filter(
                TenantProductEntitlement.tenant_id == tenant_id,
                TenantProductEntitlement.product_code == product_code,
                TenantProductEntitlement.status == "active",
            )
            .order_by(TenantProductEntitlement.created_at_utc.desc())
            .first()
        )
        assert entitlement is not None
        entitlement.valid_until_utc = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()


def test_f8_frozen_funnel_prescan_quick_full_validation_same_initial_scan(client):
    registered = client.post(
        "/tenant/register",
        json={"environment_name": "BC Cloud", "app_version": "1.0.2.29-f8", "preferred_language": "de"},
    )
    assert registered.status_code == 200, registered.text
    tenant = registered.json()
    headers = _headers(tenant)

    profile = client.put(
        "/tenant/lifecycle-profile",
        headers=headers,
        json={"primary_notification_email": "f8.funnel@example.com", "preferred_language": "de"},
    )
    assert profile.status_code == 200, profile.text

    initial = client.get("/license/status", headers=headers)
    assert initial.status_code == 200
    assert initial.json()["scan_credits_available"] == 1
    assert initial.json()["can_run_deep_scan"] is True
    assert initial.json()["can_view_issue_details"] is False
    assert initial.json()["can_view_quick_assessment"] is False
    assert initial.json()["preferred_report_variant"] == "free-health"

    # Fiverr can sell/grant Quick before the first included scan exists.
    with SessionLocal() as db:
        quick = grant_quick_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="F8-FIV-QUICK-001",
            actor="f8-funnel-test",
        )
        db.commit()
        assert quick["scan_id"] is None
        assert quick["valid_until_utc"] is None
        assert quick["scan_credit_granted"] is False

        entitlement = db.query(TenantProductEntitlement).filter(
            TenantProductEntitlement.tenant_id == tenant["tenant_id"],
            TenantProductEntitlement.product_code == PRODUCT_QUICK_ASSESSMENT,
        ).one()
        assert entitlement.valid_until_utc is None

    quick_before_scan = client.get("/license/status", headers=headers)
    assert quick_before_scan.status_code == 200
    assert quick_before_scan.json()["can_view_quick_assessment"] is True
    assert quick_before_scan.json()["scan_credits_available"] == 1
    assert quick_before_scan.json()["preferred_report_variant"] == "quick-assessment"

    initial_scan_id = "F8-FUNNEL-INITIAL-0001"
    started = client.post(
        "/scan/start",
        headers=headers,
        json={
            "tenant_id": tenant["tenant_id"],
            "run_id": initial_scan_id,
            "scan_mode": "deep",
            "total_modules": 10,
            "company_name": "F8 Funnel GmbH",
            "environment_name": "BC Cloud",
        },
    )
    assert started.status_code == 200, started.text
    assert started.json()["credit_consumed"] is True
    _complete_scan(initial_scan_id, score=66, total_records=90_000, generated_at=datetime.now(timezone.utc) - timedelta(hours=2))

    quick_status = client.get("/license/status", headers=headers)
    assert quick_status.status_code == 200
    assert quick_status.json()["scan_credits_available"] == 0
    assert quick_status.json()["can_run_deep_scan"] is False
    assert quick_status.json()["can_view_quick_assessment"] is True
    assert quick_status.json()["can_view_issue_details"] is False
    assert quick_status.json()["quick_assessment_access_until"] is None
    assert quick_status.json()["preferred_report_variant"] == "quick-assessment"
    assert client.get(f"/reports/quick-assessment/{initial_scan_id}", headers=headers).status_code == 200
    assert client.get(f"/reports/assessment/{initial_scan_id}", headers=headers).status_code == 402
    resolved = client.get(f"/reports/{initial_scan_id}/preferred-variant", headers=headers)
    assert resolved.status_code == 200
    assert resolved.json()["report_variant"] == "quick-assessment"

    with SessionLocal() as db:
        with pytest.raises(ValueError):
            grant_validation(
                db,
                tenant_id=tenant["tenant_id"],
                sales_channel="fiverr",
                external_order_reference="F8-FIV-VAL-TOO-EARLY",
                actor="f8-funnel-test",
            )

    with SessionLocal() as db:
        assessment = grant_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="F8-FIV-FULL-001",
            actor="f8-funnel-test",
        )
        db.commit()
        assert assessment["scan_id"] == initial_scan_id
        assert assessment["scan_credit_granted"] is False

    full_status = client.get("/license/status", headers=headers)
    assert full_status.status_code == 200
    assert full_status.json()["assessment_access_active"] is True
    assert full_status.json()["can_view_quick_assessment"] is True
    assert full_status.json()["can_view_issue_details"] is True
    assert full_status.json()["preferred_report_variant"] == "assessment"
    assert client.get(f"/reports/assessment/{initial_scan_id}", headers=headers).status_code == 200
    resolved = client.get(f"/reports/{initial_scan_id}/preferred-variant", headers=headers)
    assert resolved.json()["report_variant"] == "assessment"

    with SessionLocal() as db:
        assert db.query(Scan).filter(Scan.tenant_id == tenant["tenant_id"]).count() == 1

    # Full expires back to the permanently purchased Quick layer, never back to Free.
    _expire_entitlement(tenant["tenant_id"], PRODUCT_ASSESSMENT)
    expired_full = client.get("/license/status", headers=headers)
    assert expired_full.json()["assessment_access_active"] is False
    assert expired_full.json()["can_view_issue_details"] is False
    assert expired_full.json()["can_view_quick_assessment"] is True
    assert expired_full.json()["preferred_report_variant"] == "quick-assessment"
    assert client.get(f"/reports/assessment/{initial_scan_id}", headers=headers).status_code == 402
    assert client.get(f"/reports/quick-assessment/{initial_scan_id}", headers=headers).status_code == 200

    with SessionLocal() as db:
        validation = grant_validation(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="F8-FIV-VAL-001",
            actor="f8-funnel-test",
        )
        db.commit()
        assert validation["baseline_scan_id"] == initial_scan_id
        assert validation["scan_credit_granted"] is True
        assert validation["access_starts_after_validation_scan"] is True

    validation_available = client.get("/license/status", headers=headers)
    assert validation_available.json()["validation_access_active"] is False
    assert validation_available.json()["scan_credits_available"] == 1
    assert validation_available.json()["can_run_deep_scan"] is True
    assert validation_available.json()["can_view_quick_assessment"] is True

    validation_scan_id = "F8-FUNNEL-VALIDATION-0002"
    validation_started = client.post(
        "/scan/start",
        headers=headers,
        json={
            "tenant_id": tenant["tenant_id"],
            "run_id": validation_scan_id,
            "scan_mode": "deep",
            "total_modules": 10,
            "company_name": "F8 Funnel GmbH",
            "environment_name": "BC Cloud",
        },
    )
    assert validation_started.status_code == 200, validation_started.text
    assert validation_started.json()["credit_consumed"] is True
    _complete_scan(validation_scan_id, score=84, total_records=90_000, generated_at=datetime.now(timezone.utc))

    validation_active = client.get("/license/status", headers=headers)
    assert validation_active.json()["validation_access_active"] is True
    assert validation_active.json()["can_view_issue_details"] is True

    validation_resolved = client.get(f"/reports/{validation_scan_id}/preferred-variant", headers=headers)
    assert validation_resolved.status_code == 200
    assert validation_resolved.json()["report_variant"] == "validation"

    initial_resolved = client.get(f"/reports/{initial_scan_id}/preferred-variant", headers=headers)
    assert initial_resolved.status_code == 200
    assert initial_resolved.json()["report_variant"] == "assessment"

    validation_report = client.get(f"/reports/validation/{validation_scan_id}", headers=headers)
    assert validation_report.status_code == 200, validation_report.text
    assert validation_report.json()["baseline_scan_id"] == initial_scan_id
    assert validation_report.json()["validation_scan_id"] == validation_scan_id

    with SessionLocal() as db:
        assert db.query(Scan).filter(Scan.tenant_id == tenant["tenant_id"]).count() == 2
        consumed = db.query(TenantScanCredit).filter(
            TenantScanCredit.tenant_id == tenant["tenant_id"],
            TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
            TenantScanCredit.consumed_scan_id == validation_scan_id,
        ).one()
        assert consumed.status == "consumed"
        assert consumed.consumed_at_utc is not None
