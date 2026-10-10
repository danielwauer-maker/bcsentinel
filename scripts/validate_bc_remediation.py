from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "bc-extension" / "app" / "src"


def text(relative: str) -> str:
    path = BASE / relative
    assert path.exists(), f"Missing remediation artifact: {relative}"
    return path.read_text(encoding="utf-8-sig")


def require(haystack: str, *needles: str) -> None:
    for needle in needles:
        assert needle in haystack, f"Missing required remediation contract fragment: {needle}"


def main() -> None:
    enums = text("enums/DHRemediationEnums.al")
    action = text("tables/DHRemediationAction.Table.al")
    audit = text("tables/DHRemediationAudit.Table.al")
    mgt = text("codeunits/DHRemediationMgt.Codeunit.al")
    list_page = text("pages/DHRemediationActions.Page.al")
    card_page = text("pages/DHRemediationActionCard.Page.al")
    audit_page = text("pages/DHRemediationAudit.Page.al")
    permissions = text("permissionsets/BCSentinelPermissionSets.al")

    require(enums, '"DH Remediation Status"', 'Open', 'InProgress', 'Blocked', 'Completed', 'Cancelled')
    require(enums, '"DH Remediation Priority"', 'Critical', 'High', 'Medium', 'Low')
    require(enums, '"DH Remediation Source"', 'Manual', 'Recommendation', 'Imported')

    for field in [
        '"Action ID"', '"Tenant ID"', '"Company ID"', '"Finding Key"', 'Title',
        'Status', 'Priority', '"Created At UTC"', '"Updated At UTC"',
        '"Owner Principal ID"', '"Owner Display Name"', '"Due At UTC"', '"Blocked Reason"',
        '"Completion Note"', '"Validation Result Ref"', 'Source'
    ]:
        assert field in action, f"Missing action field: {field}"

    require(action,
            'Setup."Tenant ID"', 'CompanyName()', 'CreateGuid()',
            'TableRelation = User."User Security ID"',
            'UserRecord.Get("Owner Principal ID")',
            'UserRecord."Full Name"', 'UserRecord."User Name"',
            "WriteAudit(Rec, 'owner_principal_id'", "WriteAudit(Rec, 'owner_display_name'",
            "WriteAudit(Rec, 'due_at_utc'", "WriteAudit(Rec, 'blocked_reason'",
            "WriteAudit(Rec, 'completion_note'",
            'Cancel the action instead of deleting it', 'The Action ID is immutable')

    require(audit,
            '"Action ID"', '"Changed At UTC"', '"Changed By Principal ID"',
            '"Tenant ID"', '"Company ID"', '"Changed Field or Status"',
            '"Previous Value"', '"New Value"', 'immutable')

    require(mgt,
            'ValidateStatusTransition', 'OldStatus::Open', 'OldStatus::InProgress',
            'OldStatus::Blocked', 'OldStatus::Completed', 'OldStatus::Cancelled',
            'SeedFromDashboardIssue', 'LinkValidationResult', 'WriteAudit')

    # No autonomous remediation: seeding exists only as an explicit callable BC operation;
    # there is no scan-trigger subscriber or automatic status coupling in this module.
    assert '[EventSubscriber' not in mgt
    assert 'Validation Result Ref" := ValidationResultRef' in mgt
    assert 'Status :=' not in mgt.split('procedure LinkValidationResult', 1)[1]

    require(list_page, 'PageType = List', 'CardPageId = "DH Remediation Action Card"', 'DeleteAllowed = false')
    require(card_page,
            'PageType = Card', 'field(Owner; Rec."Owner Principal ID")',
            'Select the Business Central user responsible for this remediation action',
            'field("Owner Display Name"; Rec."Owner Display Name")', 'Editable = false',
            '"Validation Result Ref"', 'Audit Trail')
    require(audit_page, 'Editable = false', 'InsertAllowed = false', 'ModifyAllowed = false', 'DeleteAllowed = false')

    require(permissions,
            'tabledata "DH Remediation Action" = R,',
            'tabledata "DH Remediation Action" = RIM,',
            'tabledata "DH Remediation Audit" = R,',
            'page "DH Remediation Actions" = X',
            'page "DH Remediation Action Card" = X',
            'page "DH Remediation Audit" = X',
            'codeunit "DH Remediation Mgt." = X')

    print("BC remediation implementation contract: PASS")


if __name__ == "__main__":
    main()
