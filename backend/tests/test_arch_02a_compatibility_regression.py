from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.services import access_control_service


def _tenant() -> SimpleNamespace:
    return SimpleNamespace(
        tenant_id="tenant-regression",
        bc_company_id="company-regression",
        entra_tenant_id="entra-regression",
        bc_environment_name="Sandbox",
        bc_environment_type="sandbox",
        bc_company_name="CRONUS",
    )


def _legacy_access(**overrides):
    access = {
        "premium_active": True,
        "premium_access_until": "2026-08-01T00:00:00Z",
        "monitoring_access_until": None,
        "monitoring_active": False,
        "can_view_dashboard": True,
        "can_view_issue_details": True,
        "can_view_issues": True,
        "can_view_executive_report": True,
        "can_view_reports": True,
        "can_use_monitoring": False,
        "can_run_deep_scan": True,
        "can_run_data_health_score": False,
        "dashboard_access_until": "2026-08-01T00:00:00Z",
        "issue_access_until": "2026-08-01T00:00:00Z",
        "report_access_until": "2026-08-01T00:00:00Z",
        "assessment_access_active": True,
        "full_analysis_access_active": True,
        "validation_access_active": False,
        "validation_check_access_active": False,
        "free_access_permanent": False,
        "has_completed_data_health_score": False,
    }
    access.update(overrides)
    return access


def test_snapshot_ttl_and_legacy_capabilities_remain_unchanged(monkeypatch) -> None:
    fixed_now = datetime(2026, 7, 25, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(
        access_control_service,
        "build_product_access_snapshot",
        lambda _db, _tenant: _legacy_access(),
    )

    snapshot = access_control_service.build_authoritative_access_snapshot(
        object(),
        _tenant(),
        now=fixed_now,
    )

    expires_at = datetime.fromisoformat(snapshot["snapshot_expires_at_utc"])
    assert expires_at - fixed_now == timedelta(seconds=access_control_service.ACCESS_SNAPSHOT_TTL_SECONDS)
    assert snapshot["cache_ttl_seconds"] == access_control_service.ACCESS_SNAPSHOT_TTL_SECONDS

    capabilities = snapshot["capabilities"]
    assert capabilities[access_control_service.CAPABILITY_PRODUCT]["granted"] is True
    assert capabilities[access_control_service.CAPABILITY_DASHBOARD]["granted"] is True
    assert capabilities[access_control_service.CAPABILITY_ISSUES]["granted"] is True
    assert capabilities[access_control_service.CAPABILITY_REPORT]["granted"] is True
    assert capabilities[access_control_service.CAPABILITY_MONITORING]["granted"] is False
    assert capabilities[access_control_service.CAPABILITY_SCAN_START]["granted"] is True


def test_product_model_is_additive_and_does_not_replace_capabilities(monkeypatch) -> None:
    monkeypatch.setattr(
        access_control_service,
        "build_product_access_snapshot",
        lambda _db, _tenant: _legacy_access(validation_access_active=True),
    )

    snapshot = access_control_service.build_authoritative_access_snapshot(object(), _tenant())

    assert "capabilities" in snapshot
    assert "product_model" in snapshot
    assert snapshot["product_model"]["commercial_offers"] == ["assessment", "validation"]
    assert snapshot["product_model"]["compatibility_source"] == "product_license_service"
    assert snapshot["capabilities"][access_control_service.CAPABILITY_PRODUCT]["granted"] is True


def test_unknown_or_inactive_product_context_remains_locked(monkeypatch) -> None:
    monkeypatch.setattr(
        access_control_service,
        "build_product_access_snapshot",
        lambda _db, _tenant: _legacy_access(
            premium_active=False,
            premium_access_until=None,
            can_view_dashboard=False,
            can_view_issue_details=False,
            can_view_issues=False,
            can_view_executive_report=False,
            can_view_reports=False,
            can_run_deep_scan=False,
            assessment_access_active=False,
            full_analysis_access_active=False,
        ),
    )

    snapshot = access_control_service.build_authoritative_access_snapshot(object(), _tenant())

    assert snapshot["product_model"]["commercial_offers"] == []
    assert snapshot["product_model"]["experience_mode"] == "locked"
    assert snapshot["product_model"]["access_state"] == "locked"
    assert snapshot["capabilities"][access_control_service.CAPABILITY_PRODUCT]["granted"] is False
