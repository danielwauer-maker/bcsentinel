from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BC = ROOT / "bc-extension/app/src"


def _text(path: str) -> str:
    return (BC / path).read_text(encoding="utf-8-sig")


def test_issue_30_preserves_finding_context_and_standard_remediation_actions() -> None:
    drilldown = _text("codeunits/DHIssueDrilldownMgt.Codeunit.al")
    remediation = _text("codeunits/DHGenericRemediation.Codeunit.al")
    standard_pages = _text("pageextensions/DHStandardFindingRemediation.PageExt.al")

    assert 'RemediationContext.SetIssueCode(IssueCode);' in drilldown
    assert 'procedure PromptExclude' in remediation
    assert 'procedure MarkCorrected' in remediation
    assert "Page \"DH Exception Dialog\"" in remediation
    assert "IssueContextMissingErr" in remediation

    for page_name in (
        'Sales Order List',
        'Purchase Order List',
        'Customer Ledger Entries',
        'Vendor Ledger Entries',
        'General Ledger Entries',
        'G/L Account List',
        'Contact List',
        'Employee List',
        'Resource List',
        'Service Item List',
        'Job List',
    ):
        assert f'extends "{page_name}"' in standard_pages

    assert standard_pages.count("Caption = 'Exclude from Analysis'") >= 10
    assert standard_pages.count("Caption = 'Mark as Corrected'") >= 10


def test_issue_31_correction_status_is_persistent_visible_and_reopenable() -> None:
    remediation = _text("codeunits/DHGenericRemediation.Codeunit.al")
    corrections = _text("pages/DHCorrections.Page.al")

    assert "'CORRECTED'" in remediation
    assert "'REOPENED'" in remediation
    assert 'procedure IsCorrectionActive' in remediation
    assert 'procedure ReopenCorrection' in remediation
    assert 'UsageCategory = History;' in corrections
    assert "Caption = 'BCSentinel Corrections';" in corrections
    assert "Caption = 'Reopen Correction';" in corrections
    assert 'future scans' in corrections.lower()
    assert 'does not suppress a finding' in corrections.lower()


def test_issue_32_monitoring_end_is_authoritative_for_effective_product_access() -> None:
    setup_ext = _text("pageextensions/DHSetupEffectiveAccess.PageExt.al")

    assert 'modify(PremiumUntil)' in setup_ext
    assert 'Visible = false;' in setup_ext
    assert "Rec.\"Monitoring Active\" and (Rec.\"Monitoring Until\" <> '')" in setup_ext
    assert 'EffectiveProductAccessUntilTxt := Rec."Monitoring Until"' in setup_ext
    assert 'EffectiveProductAccessUntilTxt := Rec."Premium Until"' in setup_ext
    assert "Caption = 'Product Access Until';" in setup_ext


def test_permission_sets_include_new_cleanup_runtime_objects() -> None:
    permissions = _text("permissionsets/BCSentinelPermissionSets.al")
    for object_name in (
        'page "DH Corrections" = X',
        'codeunit "DH Remediation Context" = X',
        'codeunit "DH Generic Remediation" = X',
    ):
        assert object_name in permissions
