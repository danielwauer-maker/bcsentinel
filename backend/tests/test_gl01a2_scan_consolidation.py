from pathlib import Path

import pytest
from fastapi import HTTPException

from app.db import SessionLocal
from app.models import CreditLedgerEntry, Scan, ScanIssueRecord, ScanRunStatus, ScanStartRequest
from app.routers.scans import _normalize_scan_type


ROOT = Path(__file__).resolve().parents[2]
AL = ROOT / "bc-extension" / "app" / "src"


def _al(relative_path: str) -> str:
    return (AL / relative_path).read_text(encoding="utf-8")


def _scan_counts(tenant_id: str) -> tuple[int, int, int, int, int]:
    with SessionLocal() as db:
        return (
            db.query(Scan).filter_by(tenant_id=tenant_id).count(),
            db.query(ScanRunStatus).filter_by(tenant_id=tenant_id).count(),
            db.query(ScanStartRequest).filter_by(tenant_id=tenant_id).count(),
            db.query(CreditLedgerEntry).filter_by(tenant_id=tenant_id).count(),
            db.query(ScanIssueRecord).join(Scan, Scan.scan_id == ScanIssueRecord.scan_id).filter(Scan.tenant_id == tenant_id).count(),
        )


def test_retired_quick_endpoint_creates_no_data(client, tenant_factory):
    tenant = tenant_factory()
    before = _scan_counts(tenant["tenant_id"])

    response = client.post(
        "/scan/quick",
        headers={"X-Tenant-Id": tenant["tenant_id"], "X-Api-Token": tenant["api_token"]},
        json={"tenant_id": tenant["tenant_id"], "bc_run_id": "QUICK_MUST_NOT_EXIST"},
    )

    assert response.status_code == 410
    assert "POST /scan/start" in response.json()["detail"]
    assert _scan_counts(tenant["tenant_id"]) == before


def test_all_productive_al_entrypoints_use_deep_scan_manager():
    dashboard = _al("pages/DHDashboardList.Page.al")
    setup = _al("pages/DHSetup.Page.al")
    scheduler = _al("codeunits/DHScanSchedulerMgt.Codeunit.al")
    api_client = _al("codeunits/DHApiClient.Codeunit.al")

    assert 'Codeunit "DH Scan Dispatcher"' in dashboard
    assert "QueueDataHealthScore" in setup
    assert "QueueDeepScan(Setup)" in setup
    assert "QueueDeepScanInBackground(Setup)" in scheduler
    assert "/scan/quick" not in api_client
    assert not (AL / "codeunits" / "DHQuickScanMgt.Codeunit.al").exists()


def test_manual_and_scheduled_trigger_contexts_are_separated():
    manager = _al("codeunits/DHDeepScanMgt.Codeunit.al")
    trigger = _al("enums/DHScanTriggerContext.Enum.al")

    assert 'Enum::"DH Scan Trigger Context"::Manual' in manager
    assert 'Enum::"DH Scan Trigger Context"::Scheduled' in manager
    assert "TriggerContext <> TriggerContext::Manual" in manager
    assert "Confirm(ScanStartConfirmationQst, false)" in manager
    for value in ("Manual", "Scheduled", "Monitoring", "Retry", "System", "API"):
        assert f"; {value})" in trigger


@pytest.mark.parametrize(
    "trigger_type",
    ["deep", "assessment", "validation", "validation_check", "monitoring", "scheduled", "manual"],
)
def test_every_productive_trigger_is_persisted_as_deep(trigger_type):
    assert _normalize_scan_type(trigger_type) == "deep"


def test_quick_results_are_rejected_instead_of_creating_new_history():
    with pytest.raises(HTTPException) as exc_info:
        _normalize_scan_type("quick")

    assert exc_info.value.status_code == 410
