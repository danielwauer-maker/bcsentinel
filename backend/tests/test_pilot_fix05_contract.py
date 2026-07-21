from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
AL = ROOT / "bc-extension" / "app" / "src"
XLIFF_NS = {"x": "urn:oasis:names:tc:xliff:document:1.2"}


def _source(relative_path: str) -> str:
    return (AL / relative_path).read_text(encoding="utf-8")


def test_completed_history_precedes_stale_running_and_maps_sync_outcomes():
    history = _source("pages/DHDeepScanRuns.Page.al")
    result = history.split("local procedure GetResultText", 1)[1].split("local procedure GetResultStyle", 1)[0]

    assert result.index("IsDeepScanCompleted") < result.index("IsDeepScanRunning")
    assert "CompletedSyncPendingLbl" in result
    assert "CompletedSyncFailedLbl" in result
    assert "RejectedLbl" in result


def test_completed_backend_status_clears_stale_warning():
    monitor = _source("pages/DHDeepScanMonitor.Page.al")
    warning = monitor.split("local procedure GetDisplayWarningText", 1)[1].split("local procedure GetBackendSyncStatusText", 1)[0]

    assert warning.index("'completed', 'completed_with_warnings'") < warning.index("IsBackendNonTerminal")
    assert "BackendStatusOutdatedLbl" in warning
    assert "Backend status is outdated. The local scan completed successfully." in monitor
    scan_status = monitor.split("local procedure GetScanStatusText", 1)[1].split("local procedure GetScanStatusStyle", 1)[0]
    assert scan_status.index("'rejected'") < scan_status.index("Rec.Status = Rec.Status::Failed")


def test_iso_utc_timestamps_are_parsed_before_legacy_wall_clock_fallback():
    client = _source("codeunits/DHApiClient.Codeunit.al")
    parser = client.split("local procedure ParseJsonDateTime", 1)[1].split("local procedure FormatJsonDateTimeText", 1)[0]

    assert parser.index("Evaluate(ParsedDateTime, Value, 9)") < parser.index("Value.Replace('Z', '')")
    assert "JsonResponse.Get('started_at'" in client
    assert "JsonResponse.Get('heartbeat_at'" in client
    assert "JsonResponse.Get('completed_at'" in client


def test_successful_sync_applies_authoritative_lifecycle_atomically():
    runner = _source("codeunits/DHDeepScanRunner.Codeunit.al")
    success = runner.split("DeepScanRun.Get(DeepScanRun.\"Entry No.\");", 2)[2].split("EnsureDashboardHeaderForDeepScan", 1)[0]

    assert "ApplyScanSyncLifecycleResponse" in success
    assert 'DeepScanRun.Status := DeepScanRun.Status::Completed;' in success
    assert 'DeepScanRun.\"Backend Sync Status\" := DeepScanRun.\"Backend Sync Status\"::Synchronized;' in success
    assert 'DeepScanRun.\"Backend Status\" := \'completed\';' in success
    assert 'DeepScanRun.\"Warning Message\" := \'\';' in success


def test_manual_business_hours_confirmation_is_before_any_scan_start():
    setup = _source("pages/DHSetup.Page.al")
    start = setup.split("local procedure StartAvailableScan", 1)[1].split("local procedure OpenLatestMonitor", 1)[0]

    prompt_at = start.index("StrMenu(ManualScanActionsLbl, 2, ManualScanBusinessHoursQst)")
    assert prompt_at < start.index("QueueDataHealthScore")
    assert prompt_at < start.index("QueueDeepScan")
    assert "not Rec.\"Monitoring Active\"" in start
    assert "080000T" in start and "180000T" in start
    assert "ManualScanBusinessHoursQst" not in _source("codeunits/DHScanSchedulerMgt.Codeunit.al")


def test_full_analysis_wording_does_not_imply_scan_authorization():
    setup_table = _source("tables/DHSetup.Table.al")

    assert "Label 'Premium access active'" in setup_table
    assert "Paid scan access active" not in setup_table


def test_fix05_changed_captions_have_complete_german_targets():
    german = ET.parse(ROOT / "bc-extension" / "Translations" / "BCSentinel.de-DE.xlf")
    targets = {
        unit.find("x:source", XLIFF_NS).text: (unit.find("x:target", XLIFF_NS).text or "").strip()
        for unit in german.findall(".//x:trans-unit", XLIFF_NS)
        if unit.find("x:source", XLIFF_NS) is not None and unit.find("x:target", XLIFF_NS) is not None
    }
    required = {
        "Already used",
        "Product Access Until",
        "Monitoring Until",
        "Completed",
        "Current Module",
        "Started At",
        "Finished At",
        "Headline",
        "Less than 1 minute",
        "Open Analytics-Dashboard",
        "Premium access active",
        "Completed; synchronization pending",
        "Rejected",
        "The scan may affect system performance depending on data volume. Do you want to start it now during business hours?",
        "Start now,Cancel",
    }

    assert required <= targets.keys()
    assert all(targets[source] for source in required)
