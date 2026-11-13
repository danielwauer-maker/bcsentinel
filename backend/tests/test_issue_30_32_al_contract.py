"""Issues #30/#32: targeted AL source contracts; real BC27 SaaS acceptance remains required."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "bc-extension/app/src"
PURCHASE = ROOT / "pages/DHPurchaseLineIssueWorklist.Page.al"
SALES = ROOT / "pages/DHSalesLineIssueWorklist.Page.al"
EFFECTIVE_ACCESS = ROOT / "pageextensions/DHSetupEffectiveAccess.PageExt.al"
DISPATCHER = ROOT / "codeunits/DHIssueDrilldownDispatcher.Codeunit.al"


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def test_issue30_purchase_line_actions_bind_to_the_finding_line_not_item_master():
    page = source(PURCHASE)
    assert "action(ExcludeFinding)" in page
    assert "action(MarkIssueCorrected)" in page
    assert "action(OpenCorrectionHistory)" in page
    assert 'Database::"Purchase Line", Rec.SystemId' in page
    assert 'Remediation.PromptExclude(Database::"Purchase Line", Rec.SystemId' in page
    assert 'Remediation.MarkCorrected(Database::"Purchase Line", Rec.SystemId' in page
    assert 'Remediation.OpenHistory(Database::"Purchase Line", Rec.SystemId, CurrentIssueCode)' in page
    assert "MarkLinkedMasterRecordCorrected" not in page
    assert "ExceptionMgt.MarkItemCorrected" not in page
    assert "EnsureIssueContext();" in page
    assert "Context.SetIssueCode(CurrentIssueCode);" in page


def test_issue30_purchase_document_link_and_sales_line_exclusion():
    purchase = source(PURCHASE)
    sales = source(SALES)
    assert 'field("Document No."; Rec."Document No.")' in purchase
    assert "DrillDown = true;" in purchase
    assert "trigger OnDrillDown()" in purchase
    assert 'Page.Run(Page::"Purchase Order", PurchaseHeader);' in purchase
    assert 'Remediation.PromptExclude(Database::"Sales Line", Rec.SystemId' in sales
    assert 'IssueDrilldownDispatcher.OpenByIssueCode(IssueCode);' in source(
        ROOT / "codeunits/DHIssueDrilldownMgt.Codeunit.al"
    )
    dispatcher = source(DISPATCHER)
    assert "PurchaseWorklist.SetIssueCode(IssueCodeUpper);" in dispatcher
    assert "SalesWorklist.SetIssueCode(IssueCodeUpper);" in dispatcher


def test_issue32_monitoring_expiry_overrides_full_expiry_without_changing_entitlement():
    page = source(EFFECTIVE_ACCESS)
    assert "modify(PremiumUntil)" in page
    assert "Visible = false;" in page
    assert "field(EffectiveProductAccessUntil; EffectiveProductAccessUntilTxt)" in page
    assert "field(FullAnalysisAccessUntil; Rec.\"Premium Until\")" in page
    assert "Caption = 'Full Analysis Access Until';" in page
    assert "if Rec.\"Monitoring Active\" and (Rec.\"Monitoring Until\" <> '') then" in page
    assert 'EffectiveProductAccessUntilTxt := Rec."Monitoring Until"' in page
    assert 'EffectiveProductAccessUntilTxt := Rec."Premium Until"' in page
    assert "Rec.\"Monitoring Until\" :=" not in page
    assert "Rec.\"Premium Until\" :=" not in page
