from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LIST_PAGE = ROOT / "bc-extension/app/src/pages/DHDeepScanFindingsList.Page.al"
PART_PAGE = ROOT / "bc-extension/app/src/pages/DHDeepScanFindings.Page.al"


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def test_free_findings_are_aggregated_and_masked() -> None:
    for path in (LIST_PAGE, PART_PAGE):
        source = _source(path)
        assert "SourceTableTemporary = true;" in source
        assert "AddFreeAggregate" in source
        assert 'Rec.SetRange(Category, SourceFinding.Category);' in source
        assert 'Rec.SetRange(Severity, SourceFinding.Severity);' in source
        assert 'ProtectedImpactLbl: Label \'•••• EUR\';' in source
        assert "if not ShowPremiumDetails then\n            exit(ProtectedImpactLbl);" in source


def test_free_findings_do_not_expose_check_details_or_drilldown() -> None:
    for path in (LIST_PAGE, PART_PAGE):
        source = _source(path)
        assert 'field("Issue Code";' not in source
        assert 'field("Recommendation Preview";' not in source
        assert 'field(Title; CatalogTitle)' in source
        assert 'Visible = ShowPremiumDetails;' in source
        assert 'field(FreeAffectedCount; Rec."Affected Count")' in source
        assert 'Visible = ShowFreeSummary;' in source
        free_count_block = source.split('field(FreeAffectedCount; Rec."Affected Count")', 1)[1].split('field("Affected Count"; Rec."Affected Count")', 1)[0]
        assert "OnDrillDown" not in free_count_block


def test_full_findings_keep_title_count_and_real_impact() -> None:
    for path in (LIST_PAGE, PART_PAGE):
        source = _source(path)
        assert "IssueDrilldownMgt.OpenDeepScanFinding(Rec);" in source
        assert 'field("Affected Count"; Rec."Affected Count")' in source
        assert 'CurrencyMgt.FormatLocalAmount(Rec."Estimated Impact (EUR)")' in source
        assert 'CatalogTitle := CheckCatalogMgt.ResolveTitle(Rec."Issue Code");' in source
