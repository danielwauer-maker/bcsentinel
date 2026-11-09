"""Static AL evidence wiring; a real BC runtime test remains required."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_count_checks_record_observed_status_without_inferring_absence():
    runner = (ROOT / "bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al").read_text(encoding="utf-8-sig")
    body = runner.split("local procedure AddCountFinding", 1)[1].split("local procedure RecordCheckExecution", 1)[0]
    assert "IsCheckEnabled(IssueCode)" in body
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
        assert f"RecordCompletedCheck(DeepScanRun.\"Entry No.\", '{code}')" in runner
    helper = runner.split("local procedure RecordCompletedCheck", 1)[1].split("local procedure RecordCheckExecution", 1)[0]
    assert 'Finding.SetRange("Deep Scan Entry No.", RunEntryNo)' in helper
    assert 'Finding.SetRange("Issue Code", IssueCode)' in helper
