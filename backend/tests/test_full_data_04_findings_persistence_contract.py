from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AL_ROOT = ROOT / "bc-extension" / "app" / "src"


def _al(relative_path: str) -> str:
    return (AL_ROOT / relative_path).read_text(encoding="utf-8-sig")


def test_completion_requires_one_persisted_row_per_detected_finding():
    runner = _al("codeunits/DHDeepScanRunner.Codeunit.al")
    integrity = _al("codeunits/DHFindingsIntegrityMgt.Codeunit.al")

    assert 'FindingsIntegrityMgt.AssertExpectedFindingsPersisted(DeepScanRun, IssuesCount);' in runner
    assert 'codeunit 53350 "DH Findings Integrity Mgt."' in integrity
    assert 'Finding.SetRange("Deep Scan Entry No.", DeepScanEntryNo);' in integrity
    assert 'ActualFindingCount = ExpectedFindingCount' in integrity
    assert 'findings_persistence_mismatch' in integrity


def test_completed_history_surfaces_missing_details_without_recreating_them():
    integrity = _al("codeunits/DHFindingsIntegrityMgt.Codeunit.al")
    findings_list = _al("pages/DHDeepScanFindingsList.Page.al")
    findings_part = _al("pages/DHDeepScanFindings.Page.al")

    assert 'DeepScanRun.Status <> DeepScanRun.Status::Completed' in integrity
    assert 'No findings have been recreated.' in integrity
    assert 'FindingsIntegrityMgt.GetMissingDetailsMessage(DeepScanEntryNoFilter)' in findings_list
    assert 'MissingDetailsVisible' in findings_part
    assert 'FindingsIntegrityMgt.GetMissingDetailsMessage(DeepScanEntryNoFilter)' in findings_part


def test_finding_deletes_are_telemetry_audited_and_sync_does_not_delete_local_rows():
    integrity = _al("codeunits/DHFindingsIntegrityMgt.Codeunit.al")
    run_table = _al("tables/DHDeepScanRun.Table.al")
    reset = _al("codeunits/DHSandboxResetMgt.Codeunit.al")
    runner = _al("codeunits/DHDeepScanRunner.Codeunit.al")

    assert 'findings_deleted' in integrity
    assert "FindingsIntegrityMgt.LogFindingDeletion(Rec, 'deep_scan_run_delete');" in run_table
    assert "FindingsIntegrityMgt.LogFindingDeletion(DeepScanRun, 'sandbox_reset');" in reset
    sync_block = runner.split('local procedure TrySynchronizeScan', 1)[0]
    assert 'Finding.Delete' not in sync_block
