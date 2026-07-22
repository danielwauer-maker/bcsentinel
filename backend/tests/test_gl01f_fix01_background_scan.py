from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AL_ROOT = ROOT / "bc-extension/app/src"


def _source(relative_path: str) -> str:
    return (AL_ROOT / relative_path).read_text(encoding="utf-8")


def test_manual_run_now_starts_the_existing_table_bound_runner_in_a_child_session():
    scheduler = _source("codeunits/DHScanSchedulerMgt.Codeunit.al")
    manager = _source("codeunits/DHDeepScanMgt.Codeunit.al")
    runner = _source("codeunits/DHDeepScanRunner.Codeunit.al")

    manual_path = scheduler.split("local procedure StartManualScheduledScan", 1)[1].split(
        "[TryFunction]", 1
    )[0]
    assert "QueueDeepScanInNewSession(Setup)" in manual_path
    assert 'TableNo = "DH Deep Scan Run";' in runner
    assert "Session.StartSession(SessionId, Codeunit::\"DH Deep Scan Runner\", CompanyName(), DeepScanRun)" in manager
    assert "if TryProcessRun(Rec) then" in runner
    assert "ProcessRun(DeepScanRun);" in runner
    assert 'DeepScanRun."Last Heartbeat" := CurrentDateTime();' in runner
    assert 'DeepScanRun."Progress %" := 99;' in runner
    assert 'DeepScanRun.Status := DeepScanRun.Status::Completed;' in runner
    assert 'DeepScanRun."Progress %" := 100;' in runner


def test_rejected_background_session_start_marks_the_accepted_run_failed_before_error():
    manager = _source("codeunits/DHDeepScanMgt.Codeunit.al")
    start_session = manager.split("local procedure StartDeepScanSession", 1)[1].split(
        "local procedure RefreshActiveRunsFromBackend", 1
    )[0]

    assert "if Session.StartSession" in start_session
    assert "DeepScanFailure.MarkRunAsFailed(DeepScanRun, BackgroundSessionStartErr);" in start_session
    assert start_session.index("MarkRunAsFailed") < start_session.index("Error(BackgroundSessionStartErr)")


def test_early_child_session_error_is_persisted_and_releases_local_lease_after_backend_failure():
    runner = _source("codeunits/DHDeepScanRunner.Codeunit.al")
    failure = _source("codeunits/DHDeepScanFailure.Codeunit.al")
    on_run = runner.split("trigger OnRun()", 1)[1].split("[TryFunction]", 1)[0]

    assert "GetLastErrorText()" in on_run
    assert "ClearLastError();" in on_run
    assert "DeepScanFailure.MarkRunAsFailed(Rec, FailureText);" in on_run
    assert 'DeepScanRun.Status := DeepScanRun.Status::Failed;' in failure
    assert 'DeepScanRun."Backend Status" := \'failed\';' in failure
    assert failure.index("TryUpdateBackendFailure(DeepScanRun);") < failure.index(
        'Clear(DeepScanRun."Lease Expires At");'
    )
    assert 'Clear(DeepScanRun."Execution Token");' in failure


def test_automatic_scheduler_keeps_its_existing_dialog_free_execution_path():
    scheduler = _source("codeunits/DHScanSchedulerMgt.Codeunit.al")
    manager = _source("codeunits/DHDeepScanMgt.Codeunit.al")
    automatic_path = scheduler.split("local procedure StartScheduledScan", 1)[1].split(
        "local procedure StartManualScheduledScan", 1
    )[0]
    background_entry = manager.split("procedure QueueDeepScanInBackground", 1)[1].split(
        "procedure QueueDeepScanInNewSession", 1
    )[0]

    assert "QueueDeepScanInBackground(Setup)" in automatic_path
    assert "QueueDeepScanInternal(Setup, Enum::\"DH Scan Trigger Context\"::Scheduled, false)" in background_entry
    assert "StartInNewSession" not in background_entry
    assert "DeepScanRunner.RunSynchronously(DeepScanRun);" in manager
    assert "procedure RunSynchronously" in _source("codeunits/DHDeepScanRunner.Codeunit.al")


def test_healthy_active_run_still_blocks_after_backend_reconciliation():
    manager = _source("codeunits/DHDeepScanMgt.Codeunit.al")
    deep_path = manager.split("local procedure QueueDeepScanInternal", 1)[1].split(
        "procedure QueueDataHealthScore", 1
    )[0]

    assert deep_path.index("RefreshActiveRunsFromBackend(Setup);") < deep_path.index(
        "FindUnacceptedRun('', DeepScanRun)"
    )
    assert deep_path.index("FindUnacceptedRun('', DeepScanRun)") < deep_path.index(
        "EnsureNoActiveScan();"
    )
    assert "Error(ScanAlreadyRunningErr);" in manager


def test_orphan_recovery_uses_existing_backend_status_and_same_run_retry_contract():
    manager = _source("codeunits/DHDeepScanMgt.Codeunit.al")
    api_client = _source("codeunits/DHApiClient.Codeunit.al")
    backend_recovery = (ROOT / "backend/app/services/scan_status_service.py").read_text(encoding="utf-8")

    refresh = manager.split("local procedure RefreshActiveRunsFromBackend", 1)[1].split(
        "[TryFunction]", 1
    )[0]
    retry = manager.split("local procedure FindUnacceptedRun", 1)[1].split(
        "local procedure CreateOrUpdateScanHeader", 1
    )[0]

    assert "TryRefreshActiveRunFromBackend(Setup, DeepScanRun)" in refresh
    assert "ApiClient.RefreshScanStatus(Setup, DeepScanRun);" in manager
    assert "recovery_required" in api_client
    assert "RetryRequired" in api_client
    assert '"Start Request Status"::RetryRequired' in retry
    assert "SCAN_STALLED_AFTER_SECONDS" in backend_recovery
    assert "SCAN_MAX_ATTEMPTS" in backend_recovery
    assert 'run.status = "queued"' in backend_recovery
    assert 'run.status = "failed"' in backend_recovery


def test_free_and_validation_starts_keep_confirmation_while_scheduled_paths_do_not():
    manager = _source("codeunits/DHDeepScanMgt.Codeunit.al")

    assert "ConfirmManualScanStart(Enum::\"DH Scan Trigger Context\"::Manual)" in manager
    assert "exit(QueueDeepScanInternal(Setup, Enum::\"DH Scan Trigger Context\"::Manual, true));" in manager
    assert "if TriggerContext <> TriggerContext::Manual then\n            exit(true);" in manager
    assert "Confirm(ScanStartConfirmationQst, false)" in manager
