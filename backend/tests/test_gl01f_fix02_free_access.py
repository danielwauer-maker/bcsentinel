from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.db import SessionLocal
from app.models import (
    Scan,
    ScanRunStatus,
    ScanStartRequest,
    Tenant,
    TenantProductEntitlement,
)
from app.services.access_control_service import build_authoritative_access_snapshot
from app.routers.billing import _allowed_checkout_product_codes
from app.services.product_license_service import (
    ONE_TIME_ACCESS_DAYS,
    build_product_access_snapshot,
)


ROOT = Path(__file__).resolve().parents[2]
FREE_CAPABILITIES = ("dashboard_access", "issues_access", "report_access")


def _store_free_run(
    tenant_id: str,
    *,
    run_id: str,
    status: str,
    completed_at: datetime | None,
    result_persisted: bool,
) -> None:
    created_at = completed_at or datetime.now(timezone.utc)
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        tenant.free_assessment_used = True
        db.add(
            Scan(
                scan_id=run_id,
                tenant_id=tenant_id,
                scan_type="data_health_score",
                generated_at_utc=created_at,
                data_score=81,
                checks_count=199,
                issues_count=3,
                premium_available=False,
                summary_headline="Free score completed",
                summary_rating="good",
                total_records=100,
            )
        )
        db.add(
            ScanStartRequest(
                tenant_id=tenant_id,
                client_request_id=f"00000000-0000-0000-0000-{run_id[-12:].lower().rjust(12, '0')}",
                payload_hash=(run_id.lower() * 64)[:64],
                scan_id=run_id,
                requested_scan_mode="data_health_score",
                resolved_product_code="data_health_score",
                free_scan_slot="data_health_score",
                status="accepted",
                created_at_utc=created_at,
                updated_at_utc=created_at,
            )
        )
        db.add(
            ScanRunStatus(
                run_id=run_id,
                tenant_id=tenant_id,
                scan_mode="data_health_score",
                status=status,
                created_at_utc=created_at,
                updated_at_utc=created_at,
                completed_at_utc=completed_at,
                result_persisted_at_utc=completed_at if result_persisted else None,
                progress_percent=100 if status.startswith("completed") else 50,
            )
        )
        db.commit()


def _snapshots(tenant_id: str) -> tuple[dict, dict]:
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).one()
        return build_product_access_snapshot(db, tenant), build_authoritative_access_snapshot(db, tenant)


def test_completed_free_scan_grants_seven_day_dashboard_findings_and_report_access(tenant_factory):
    tenant = tenant_factory()
    completed_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    _store_free_run(
        tenant["tenant_id"],
        run_id="FREE_FIX02_OK",
        status="completed",
        completed_at=completed_at,
        result_persisted=True,
    )

    access, authoritative = _snapshots(tenant["tenant_id"])
    expected_until = completed_at + timedelta(days=ONE_TIME_ACCESS_DAYS)

    assert access["free_assessment_used"] is True
    assert access["premium_active"] is False
    assert access["can_view_dashboard"] is True
    assert access["can_view_issues"] is True
    assert access["can_view_reports"] is True
    assert access["can_view_actions"] is False
    assert access["can_view_record_details"] is False
    with SessionLocal() as db:
        stored_tenant = db.query(Tenant).filter_by(tenant_id=tenant["tenant_id"]).one()
        assert "full_analysis" in _allowed_checkout_product_codes(db, stored_tenant)
    for field in ("dashboard_access_until", "issue_access_until", "report_access_until"):
        assert datetime.fromisoformat(access[field].replace("Z", "+00:00")) == expected_until
    for capability in FREE_CAPABILITIES:
        assert authoritative["capabilities"][capability]["granted"] is True
    assert authoritative["capabilities"]["product_access"]["granted"] is False
    assert authoritative["capabilities"]["monitoring_access"]["granted"] is False


@pytest.mark.parametrize("status", ["cancelled", "failed"])
def test_unsuccessful_free_scan_does_not_grant_access(tenant_factory, status):
    tenant = tenant_factory()
    _store_free_run(
        tenant["tenant_id"],
        run_id=f"FREE_{status.upper()}",
        status=status,
        completed_at=None,
        result_persisted=False,
    )

    access, authoritative = _snapshots(tenant["tenant_id"])

    assert access["free_assessment_used"] is True
    assert access["has_completed_data_health_score"] is False
    assert access["dashboard_access_until"] is None
    assert access["issue_access_until"] is None
    assert access["report_access_until"] is None
    for capability in FREE_CAPABILITIES:
        assert authoritative["capabilities"][capability]["granted"] is False


def test_license_snapshot_is_updated_immediately_after_free_completion(
    client, tenant_factory, auth_header_factory
):
    tenant = tenant_factory()
    _store_free_run(
        tenant["tenant_id"],
        run_id="FREE_IMMEDIATE",
        status="completed",
        completed_at=datetime.now(timezone.utc),
        result_persisted=True,
    )

    response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    payload = response.json()
    assert payload["dashboard_access_until"]
    assert payload["issue_access_until"]
    assert payload["product_access"]["report_access_until"]
    for capability in FREE_CAPABILITIES:
        assert payload["capabilities"][capability]["granted"] is True
    report_response = client.get(
        "/reports/executive/FREE_IMMEDIATE",
        headers=auth_header_factory(tenant),
    )
    assert report_response.status_code == 200


def test_bc_maps_all_free_access_fields_and_uses_separate_guards():
    api_client = (ROOT / "bc-extension/app/src/codeunits/DHApiClient.Codeunit.al").read_text(encoding="utf-8")
    access_guard = (ROOT / "bc-extension/app/src/codeunits/DHAccessGuard.Codeunit.al").read_text(encoding="utf-8")
    setup_table = (ROOT / "bc-extension/app/src/tables/DHSetup.Table.al").read_text(encoding="utf-8")
    setup_page = (ROOT / "bc-extension/app/src/pages/DHSetup.Page.al").read_text(encoding="utf-8")
    deep_scan_runner = (ROOT / "bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al").read_text(encoding="utf-8")

    assert "JsonResponse.Get('dashboard_access_until_bc'" in api_client
    assert "JsonResponse.Get('issue_access_until_bc'" in api_client
    assert "GetCapabilityUntil(Capabilities, 'report_access')" in api_client
    assert "Setup.\"Can View Dashboard\" := DashboardAccessGranted;" in api_client
    assert "Setup.\"Can View Issue Details\" := IssuesAccessGranted;" in api_client
    assert "Setup.\"Can View Reports\" := ReportAccessGranted;" in api_client
    assert "EnsureCapability('dashboard_access', true);" in access_guard
    assert "EnsureCapability('issues_access', true);" in access_guard
    assert "EnsureCapability('report_access', true);" in access_guard
    assert 'if "Can View Issue Details" or "Premium Enabled" then' not in setup_table
    assert 'HasOneTimeAccess :=\n            Rec."Premium Enabled" or' in setup_page
    assert "if not IsDataHealthScoreRun(DeepScanRun) then\n            TryRefreshLicenseAfterCompletion(Setup);" not in deep_scan_runner
    assert deep_scan_runner.count("TryRefreshLicenseAfterCompletion(Setup);") == 1


def test_expired_free_access_is_blocked(tenant_factory):
    tenant = tenant_factory()
    _store_free_run(
        tenant["tenant_id"],
        run_id="FREE_EXPIRED",
        status="completed",
        completed_at=datetime.now(timezone.utc) - timedelta(days=ONE_TIME_ACCESS_DAYS, seconds=1),
        result_persisted=True,
    )

    access, authoritative = _snapshots(tenant["tenant_id"])

    assert access["has_completed_data_health_score"] is True
    assert access["can_view_dashboard"] is False
    assert access["can_view_issues"] is False
    assert access["can_view_reports"] is False
    for capability in FREE_CAPABILITIES:
        assert authoritative["capabilities"][capability]["granted"] is False
        assert authoritative["capabilities"][capability]["valid_until_utc"] is not None


def test_historical_affected_tenant_is_repaired_from_original_completion_without_extension(tenant_factory):
    tenant = tenant_factory()
    completed_at = datetime.now(timezone.utc) - timedelta(days=2)
    _store_free_run(
        tenant["tenant_id"],
        run_id="FREE_HISTORIC",
        status="completed_with_warnings",
        completed_at=completed_at,
        result_persisted=True,
    )

    first, _ = _snapshots(tenant["tenant_id"])
    second, _ = _snapshots(tenant["tenant_id"])
    expected = completed_at + timedelta(days=ONE_TIME_ACCESS_DAYS)

    assert datetime.fromisoformat(first["free_access_until"].replace("Z", "+00:00")) == expected
    assert second["free_access_until"] == first["free_access_until"]


def test_paid_access_remains_authoritative_and_is_not_shortened_by_free_repair(tenant_factory):
    tenant = tenant_factory()
    now = datetime.now(timezone.utc)
    paid_until = now + timedelta(days=30)
    _store_free_run(
        tenant["tenant_id"],
        run_id="FREE_WITH_PAID",
        status="completed",
        completed_at=now - timedelta(days=1),
        result_persisted=True,
    )
    with SessionLocal() as db:
        db.add(
            TenantProductEntitlement(
                tenant_id=tenant["tenant_id"],
                product_code="full_analysis",
                status="active",
                source="fix02_regression",
                valid_until_utc=paid_until,
                created_at_utc=now,
                updated_at_utc=now,
            )
        )
        db.commit()

    access, authoritative = _snapshots(tenant["tenant_id"])

    assert access["premium_active"] is True
    assert access["can_view_actions"] is True
    assert access["can_view_record_details"] is True
    assert datetime.fromisoformat(access["dashboard_access_until"].replace("Z", "+00:00")) == paid_until
    assert authoritative["capabilities"]["product_access"]["granted"] is True
    assert authoritative["capabilities"]["monitoring_access"]["granted"] is False
