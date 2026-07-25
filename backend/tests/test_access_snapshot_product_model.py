from datetime import datetime, timezone
from types import SimpleNamespace

from app.core.product_model import Entitlement
from app.services import access_control_service


def _tenant() -> SimpleNamespace:
    return SimpleNamespace(
        tenant_id="tenant-1",
        bc_company_id="company-1",
        entra_tenant_id="entra-1",
        bc_environment_name="Sandbox",
        bc_environment_type="sandbox",
        bc_company_name="CRONUS",
    )


def _access(**overrides):
    access = {
        "premium_active": False,
        "premium_access_until": None,
        "monitoring_access_until": None,
        "monitoring_active": False,
        "can_view_dashboard": False,
        "can_view_issue_details": False,
        "can_view_issues": False,
        "can_view_executive_report": False,
        "can_view_reports": False,
        "can_use_monitoring": False,
        "can_run_deep_scan": False,
        "can_run_data_health_score": False,
        "dashboard_access_until": None,
        "issue_access_until": None,
        "report_access_until": None,
        "assessment_access_active": False,
        "full_analysis_access_active": False,
        "validation_access_active": False,
        "validation_check_access_active": False,
        "free_access_permanent": False,
        "has_completed_data_health_score": False,
    }
    access.update(overrides)
    return access


def test_monitoring_snapshot_exposes_canonical_product_context(monkeypatch) -> None:
    monkeypatch.setattr(
        access_control_service,
        "build_product_access_snapshot",
        lambda _db, _tenant: _access(
            premium_active=True,
            monitoring_active=True,
            can_view_dashboard=True,
            can_view_issue_details=True,
            can_view_issues=True,
            can_view_executive_report=True,
            can_view_reports=True,
            can_use_monitoring=True,
            can_run_deep_scan=True,
        ),
    )

    snapshot = access_control_service.build_authoritative_access_snapshot(
        object(),
        _tenant(),
        now=datetime(2026, 7, 25, tzinfo=timezone.utc),
    )

    product_model = snapshot["product_model"]
    assert snapshot["snapshot_version"] == "p0d-v2-product-model"
    assert product_model["commercial_offers"] == ["monitoring"]
    assert product_model["experience_mode"] == "monitoring"
    assert product_model["access_state"] == "active"
    assert Entitlement.MONITORING_SCHEDULE.value in product_model["entitlements"]
    assert Entitlement.MONITORING_HISTORY.value in product_model["entitlements"]


def test_assessment_and_validation_are_distinct_offers(monkeypatch) -> None:
    monkeypatch.setattr(
        access_control_service,
        "build_product_access_snapshot",
        lambda _db, _tenant: _access(
            premium_active=True,
            assessment_access_active=True,
            validation_access_active=True,
            can_view_dashboard=True,
        ),
    )

    snapshot = access_control_service.build_authoritative_access_snapshot(object(), _tenant())

    product_model = snapshot["product_model"]
    assert product_model["commercial_offers"] == ["assessment", "validation"]
    assert product_model["experience_mode"] == "validation_result"
    assert Entitlement.VALIDATION_RUN.value in product_model["entitlements"]


def test_free_and_locked_experience_modes_remain_fail_closed(monkeypatch) -> None:
    monkeypatch.setattr(
        access_control_service,
        "build_product_access_snapshot",
        lambda _db, _tenant: _access(
            free_access_permanent=True,
            has_completed_data_health_score=True,
            can_view_dashboard=True,
        ),
    )
    free_snapshot = access_control_service.build_authoritative_access_snapshot(object(), _tenant())
    assert free_snapshot["product_model"]["commercial_offers"] == []
    assert free_snapshot["product_model"]["experience_mode"] == "free"

    monkeypatch.setattr(
        access_control_service,
        "build_product_access_snapshot",
        lambda _db, _tenant: _access(),
    )
    locked_snapshot = access_control_service.build_authoritative_access_snapshot(object(), _tenant())
    assert locked_snapshot["product_model"]["experience_mode"] == "locked_preview"
    assert locked_snapshot["product_model"]["access_state"] == "locked"
