from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAGES = ROOT / "bc-extension/app/src/pages"
PAGEEXT = ROOT / "bc-extension/app/src/pageextensions"

ITEM_WORKLISTS = (
    PAGES / "DHItemMissingCostList.Page.al",
    PAGES / "DHItemMissingPriceList.Page.al",
    PAGES / "DHItemNegativeInventoryList.Page.al",
    PAGES / "DHBlockedItemsWithInventory.Page.al",
)


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def test_bcsentinel_item_worklists_have_consistent_remediation_actions() -> None:
    for path in ITEM_WORKLISTS:
        source = _source(path)
        assert "Caption = 'Open Item Card';" in source
        assert "Page.Run(Page::\"Item Card\", Rec);" in source
        assert "Caption = 'Exclude from Analysis';" in source
        assert "PromptAddItemException" in source
        assert "Caption = 'Mark as Corrected';" in source
        assert "MarkItemCorrected" in source


def test_item_number_is_direct_drilldown_to_original_card() -> None:
    for path in ITEM_WORKLISTS:
        source = _source(path)
        assert 'field("No."; Rec."No.")' in source
        assert "trigger OnDrillDown()" in source
        assert "Page.Run(Page::\"Item Card\", Rec);" in source


def test_standard_item_list_offers_context_aware_remediation_without_manual_issue_code() -> None:
    source = _source(PAGEEXT / "DHItemListExt.PageExt.al")
    assert "action(DHExcludeFromAnalysis)" in source
    assert "action(DHMarkCorrected)" in source
    assert "ResolveIssueCodeFromFilters" in source
    assert "PromptAddItemException(Rec, IssueCode)" in source
    assert "MarkItemCorrected(Rec, IssueCode" in source
    assert "Open Item Card" in source


def test_existing_customer_and_vendor_worklists_keep_direct_remediation() -> None:
    for filename in ("DHCustomerIssueList.Page.al", "DHVendorIssueList.Page.al"):
        source = _source(PAGES / filename)
        assert "Exclude from Analysis" in source
        assert "Mark as Corrected" in source
        assert "Correct Data" in source
