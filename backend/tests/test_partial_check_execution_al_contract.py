"""Static AL evidence wiring; a real BC runtime test remains required."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_count_checks_record_observed_status_without_inferring_absence():
    runner = (ROOT / "bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al").read_text(encoding="utf-8-sig")
    body = runner.split("local procedure AddCountFinding", 1)[1].split("local procedure RecordCheckExecution", 1)[0]
    assert "IsCheckEnabledForRun(DeepScanRun, IssueCode)" in body
    assert "RecordCheckExecution(DeepScanRun.\"Entry No.\", IssueCode, 'SKIPPED', 0)" in body
    assert "RecordCheckExecution(DeepScanRun.\"Entry No.\", IssueCode, 'PASS', 0)" in body
    assert "RecordCheckExecution(DeepScanRun.\"Entry No.\", IssueCode, 'FINDINGS', 1)" in body
    assert body.index("InsertFinding(") < body.index("'FINDINGS', 1")
    assert "bc-check-execution-partial-v1" in runner


def test_scan_and_scheduler_roles_have_evidence_table_access():
    permissions = (ROOT / "bc-extension/app/src/permissionsets/BCSentinelPermissionSets.al").read_text(encoding="utf-8-sig")
    for role in ("BCSENTINEL SCAN", "BCSENTINEL ADMIN", "BCSENTINEL SCHEDULER"):
        section = permissions.split(f'"{role}"', 1)[1].split("\n}", 1)[0]
        assert 'tabledata "DH Check Execution" = RIMD' in section


def test_duplicate_checks_record_only_after_their_individual_execution_path():
    runner = (ROOT / "bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al").read_text(encoding="utf-8-sig")
    codes = ("CUSTOMERS_DUPLICATE_EMAIL", "VENDORS_DUPLICATE_EMAIL", "CUSTOMERS_DUPLICATE_VAT",
             "VENDORS_DUPLICATE_VAT", "CUSTOMERS_DUPLICATE_NAME_POST_CITY", "VENDORS_DUPLICATE_NAME_POST_CITY")
    for code in codes:
        assert f"RecordCheckExecution(DeepScanRun.\"Entry No.\", '{code}', 'SKIPPED', 0)" in runner
        assert f"RecordCheckStarted(DeepScanRun.\"Entry No.\", '{code}')" in runner
        assert f"RecordCompletedCheck(DeepScanRun.\"Entry No.\", '{code}')" in runner
    helper = runner.split("local procedure RecordCompletedCheck", 1)[1].split("local procedure RecordCheckExecution", 1)[0]
    assert 'Finding.SetRange("Deep Scan Entry No.", RunEntryNo)' in helper
    assert 'Finding.SetRange("Issue Code", IssueCode)' in helper
    failure = (ROOT / "bc-extension/app/src/codeunits/DHDeepScanFailure.Codeunit.al").read_text(encoding="utf-8-sig")
    assert "CheckExecution.SetRange(\"Execution Status\", 'STARTED')" in failure
    assert "CheckExecution.\"Execution Status\" := 'FAILED'" in failure
    assert 'DeepScanRun."Backend Sync Status" := DeepScanRun."Backend Sync Status"::RetryRequired' in failure
    assert "procedure RetryFailedEvidence" in failure


def test_snapshot_is_persisted_before_start_and_acknowledged_before_run():
    management = (ROOT / "bc-extension/app/src/codeunits/DHDeepScanMgt.Codeunit.al").read_text(encoding="utf-8-sig")
    client = (ROOT / "bc-extension/app/src/codeunits/DHApiClient.Codeunit.al").read_text(encoding="utf-8-sig")
    runner = (ROOT / "bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al").read_text(encoding="utf-8-sig")
    capture = management.split("local procedure StartBackendScanWithRecovery", 1)[1].split("local procedure ShowScanResultMessage", 1)[0]
    assert capture.index("SetStartExpectationOnce") < capture.index("Commit()") < capture.index("TrySendBackendScanStart")
    start = client.split("local procedure TryStartBackendScan", 1)[1].split("local procedure GetScanStartErrorMessage", 1)[0]
    assert start.index("/scan/expectation-capabilities") < start.index("/scan/start")
    assert "JsonRequest.Add('expectation', StartExpectation)" in start
    assert "expectation_status" in client and "<> 'accepted'" in client
    process = runner.split("local procedure ProcessRun", 1)[1].split("local procedure TrySynchronizeScan", 1)[0]
    assert 'if DeepScanRun."Started At" <> 0DT then' in process
    assert process.index('if DeepScanRun."Started At" <> 0DT then') < process.index("RunChecks(")
    assert process.index("AssertStartExpectationContext(DeepScanRun)") < process.index("RunChecks(")
    assert "ApplyFrozenModules(DeepScanRun, Setup)" in runner
    assert "GetExpectedChecksCountForRun(DeepScanRun, Setup)" in runner
    assert "DeepScanFailure.RetryFailedEvidence(DeepScanRun)" in management


def test_frozen_exception_scope_has_deterministic_primary_key_order():
    source = (ROOT / "bc-extension/app/src/codeunits/DHScanCheckMgt.Codeunit.al").read_text(encoding="utf-8-sig")
    snapshot = source.split("procedure BuildStartExpectation", 1)[-1]
    before_entries = snapshot.split("ExceptionObject.Add('entry_no'", 1)[0]
    # Stable ordering is required before enumerating the exception snapshot.
    assert 'IssueException.SetCurrentKey("Entry No.");' in before_entries
    assert before_entries.index('IssueException.Reset();') < before_entries.index('IssueException.SetCurrentKey("Entry No.");')
    assert before_entries.index('IssueException.SetCurrentKey("Entry No.");') < before_entries.index('IssueException.FindSet()')


def test_backend_normalizes_frozen_exception_scope_in_same_order():
    source = (ROOT / "backend/app/routers/scans.py").read_text(encoding="utf-8")
    assert 'sorted(expected["exception_scope"], key=lambda item: item["entry_no"])' in source


def test_exception_entry_number_is_primary_key_for_snapshot_order():
    source = (ROOT / "bc-extension/app/src/tables/DHIssueException.Table.al").read_text(encoding="utf-8-sig")
    assert 'key(PK; "Entry No.")' in source



def test_individual_completion_requires_persisted_started_evidence():
    runner = (ROOT / "bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al").read_text(encoding="utf-8-sig")
    body = runner.split("local procedure RecordCompletedCheck", 1)[1].split("local procedure RecordCheckExecution", 1)[0]
    assert 'CheckExecution: Record "DH Check Execution";' in body
    assert "if not CheckExecution.Get(RunEntryNo, IssueCode) then" in body
    assert 'if CheckExecution."Execution Status" <> \'STARTED\' then' in body
    assert body.index("if not CheckExecution.Get(RunEntryNo, IssueCode) then") < body.index("Finding.Count()")


def test_snapshot_completion_requires_each_enabled_check_terminal_status():
    manager = (ROOT / "bc-extension/app/src/codeunits/DHScanCheckMgt.Codeunit.al").read_text(encoding="utf-8-sig")
    runner = (ROOT / "bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al").read_text(encoding="utf-8-sig")
    body = manager.split("procedure AssertCompletedCheckEvidenceForRun", 1)[1].split("procedure GetExpectedChecksCountForRun", 1)[0]
    assert "if DeepScanRun.GetStartExpectationText() = '' then" in body
    assert "foreach Token in Checks do begin" in body
    assert "if Value.AsValue().AsBoolean() then begin" in body
    assert 'CheckExecution.Get(DeepScanRun."Entry No.", IssueCode)' in body
    assert 'CheckExecution."Execution Status" <> \'PASS\'' in body
    assert 'CheckExecution."Execution Status" <> \'FINDINGS\'' in body
    assert "SCAN_CHECK_EVIDENCE_INCOMPLETE" in body
    run_body = runner.split("local procedure ProcessRun", 1)[1].split("local procedure TrySynchronizeScan", 1)[0]
    assert run_body.index("ExceptionMgt.EndFrozenExceptionScope()") < run_body.index("ScanCheckMgt.AssertCompletedCheckEvidenceForRun(DeepScanRun)")
    assert run_body.index("ScanCheckMgt.AssertCompletedCheckEvidenceForRun(DeepScanRun)") < run_body.index("RecalculateScoreMetrics(DeepScanRun, Score)")
    assert run_body.index("ScanCheckMgt.AssertCompletedCheckEvidenceForRun(DeepScanRun)") < run_body.index("BuildSyncPayload(Setup, DeepScanRun)")


def test_not_executed_requires_absence_of_observed_module_start():
    failure = (ROOT / "bc-extension/app/src/codeunits/DHDeepScanFailure.Codeunit.al").read_text(encoding="utf-8-sig")
    body = failure.split("local procedure ModuleDefinitelyNotStarted", 1)[1].split("procedure RetryFailedEvidence", 1)[0]
    # Module-level progress alone must not override an observed active module.
    assert 'if UpperCase(DeepScanRun."Current Module") = UpperCase(RuntimeModule) then' in body
    assert "exit(false);" in body
    assert body.index('DeepScanRun."Current Module"') < body.index("DeepScanRun.\"System Progress %\" = 0")
    for normalized in (
        "'CUSTOMER', 'VENDOR', 'LEDGER', 'FINANCE': RuntimeModule := 'Finance'",
        "'PURCHASE': RuntimeModule := 'Purchasing'",
        "'ITEM', 'INVENTORY': RuntimeModule := 'Inventory'",
        "'JOB': RuntimeModule := 'Jobs'",
    ):
        assert normalized in body
    # Unknown module names must never be optimistically classified as unstarted.
    assert body.rstrip().endswith("exit(false);\n    end;")


def test_failure_evidence_only_marks_started_checks_failed():
    failure = (ROOT / "bc-extension/app/src/codeunits/DHDeepScanFailure.Codeunit.al").read_text(encoding="utf-8-sig")
    body = failure.split("procedure MarkRunAsFailed", 1)[1].split("local procedure RecordUnreachedChecks", 1)[0]
    assert 'CheckExecution.SetRange("Execution Status", \'STARTED\')' in body
    assert "CheckExecution.\"Execution Status\" := 'FAILED';" in body
    assert "RecordUnreachedChecks(DeepScanRun)" in body
