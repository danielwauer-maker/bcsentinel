"""Source contract for first BC business-record identity producer.

Static tests only. No BC runtime, row-comparison or backend source attestation.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TABLE = ROOT / "bc-extension/app/src/tables/DHScanRecordEvidence.Table.al"
RUNNER = ROOT / "bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al"
PERMISSIONS = ROOT / "bc-extension/app/src/permissionsets/BCSentinelPermissionSets.al"


def test_record_identity_table_is_additive_and_source_bound():
    source = TABLE.read_text(encoding="utf-8-sig")
    assert 'table 53198 "DH Scan Record Evidence"' in source
    for col in ('"Run Entry No."', '"Check Code"', '"Source Table ID"', '"Source Record SystemId"'):
        assert col in source
    assert 'key(PK; "Run Entry No.", "Check Code", "Source Table ID", "Source Record SystemId")' in source
    assert "RecordSystemId = EmptyGuid" in source
    assert "if Get(RunEntryNo, CheckCode, TableId, RecordSystemId) then" in source


def test_first_producer_uses_customer_business_systemid_not_finding_systemid():
    runner = RUNNER.read_text(encoding="utf-8-sig")
    body = runner.split("local procedure CountCustomersByVat(", 1)[1].split(
        "local procedure CountVendorsByVat(", 1
    )[0]
    assert 'RecordEvidence: Record "DH Scan Record Evidence";' in body
    assert 'RecordEvidence.RecordObserved(RunEntryNo, IssueCode, Database::Customer, Customer.SystemId)' in body
    assert 'if Count > 1 then begin' in body
    assert body.index("if Count > 1 then begin") < body.index("RecordEvidence.RecordObserved(")
    assert 'if not IsCustomerDuplicateExcluded(Customer, IssueCode) then' in body
    assert 'CountCustomersByVat(DeepScanRun."Entry No.", Customer."VAT Registration No."' in runner
    assert 'RecordEvidence.RecordObserved(RunEntryNo, IssueCode, Database::Customer, Finding.SystemId)' not in runner


def test_only_scan_roles_can_write_record_identity_observations():
    source = PERMISSIONS.read_text(encoding="utf-8-sig")
    for role in ("BCSENTINEL SCAN", "BCSENTINEL ADMIN", "BCSENTINEL SCHEDULER"):
        section = source.split(f'"{role}"', 1)[1].split("\n}", 1)[0]
        assert 'tabledata "DH Scan Record Evidence" = RIMD' in section
    viewer = source.split('"BCSENTINEL VIEWER"', 1)[1].split("\n}", 1)[0]
    assert 'tabledata "DH Scan Record Evidence"' not in viewer


def test_customer_vat_group_has_fail_closed_member_count_before_completion():
    runner = RUNNER.read_text(encoding="utf-8-sig")
    vat_run = runner.split("local procedure RunCustomerDuplicateVatCheck(", 1)[1].split(
        "local procedure RunVendorDuplicateVatCheck(", 1
    )[0]
    assert "AssertCustomerVatRecordEvidenceComplete(DeepScanRun.\"Entry No.\");" in vat_run
    assert vat_run.index("AssertCustomerVatRecordEvidenceComplete(") < vat_run.index(
        "RecordCompletedCheck(DeepScanRun.\"Entry No.\", 'CUSTOMERS_DUPLICATE_VAT')"
    )
    validator = runner.split("local procedure AssertCustomerVatRecordEvidenceComplete(", 1)[1].split(
        "local procedure CountVendorsByVat(", 1
    )[0]
    assert 'Finding.SetRange("Deep Scan Entry No.", RunEntryNo)' in validator
    assert 'Finding.SetRange("Issue Code", \'CUSTOMERS_DUPLICATE_VAT\')' in validator
    assert 'ExpectedMembers += Finding."Affected Count";' in validator
    assert 'RecordEvidence.SetRange("Source Table ID", Database::Customer)' in validator
    assert "ObservedMembers := RecordEvidence.Count();" in validator
    assert "if ObservedMembers <> ExpectedMembers then" in validator
    assert "SCAN_RECORD_EVIDENCE_INCOMPLETE" in validator


def test_no_other_check_claims_record_membership_completeness():
    runner = RUNNER.read_text(encoding="utf-8-sig")
    assert runner.count("AssertCustomerVatRecordEvidenceComplete(DeepScanRun.") == 1
    assert "AssertVendorVatRecordEvidenceComplete" not in runner
