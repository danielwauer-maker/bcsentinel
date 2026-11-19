"""FULL-FIX-02: an original Free baseline can be unlocked, never recreated."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AL_ROOT = ROOT / "bc-extension" / "app" / "src"


def _al(relative_path: str) -> str:
    return (AL_ROOT / relative_path).read_text(encoding="utf-8-sig")


def test_findings_pages_load_the_physical_run_scope_into_their_temporary_view():
    findings = _al("pages/DHDeepScanFindingsList.Page.al")
    setup = _al("pages/DHSetup.Page.al")
    monitor = _al("pages/DHDeepScanMonitor.Page.al")

    assert "SourceTableTemporary = true;" in findings
    assert "DeepScanEntryNoFilter: Integer;" in findings
    assert 'SourceFinding.SetRange("Deep Scan Entry No.", DeepScanEntryNoFilter)' in findings
    assert "procedure SetDeepScanEntryNo(DeepScanEntryNo: Integer)" in findings
    assert 'FindingsPage.SetDeepScanEntryNo(DeepScanRun."Entry No.");' in setup
    assert 'FindingsPage.SetDeepScanEntryNo(Rec."Entry No.");' in monitor
    assert 'Page.Run(Page::"DH Deep Scan Findings List", Finding);' not in setup
    assert 'Page.Run(Page::"DH Deep Scan Findings List", Finding);' not in monitor


def test_free_baseline_uses_full_report_only_when_the_current_access_snapshot_allows_it():
    links = _al("codeunits/DHReportLinkMgt.Codeunit.al")
    archive = (ROOT / "backend" / "app" / "services" / "report_archive_service.py").read_text(encoding="utf-8")

    variant = links.split("procedure GetCompletedReportVariant", 1)[1].split(
        "local procedure GetReportErrorText", 1
    )[0]
    assert 'AccessGuard.HasFreshFullOrMonitoringAccess()' in variant
    assert "'data_health_score', 'free', 'free_deep':" in variant
    assert "exit('full');" in variant
    assert "exit('free');" in variant
    assert 'HTTPException(status_code=402, detail="FULL_ACCESS_INACTIVE")' in archive
    assert "archive_full_report(db, tenant, scan, company_id)" in archive


def test_scan_mode_is_persisted_and_drives_the_product_headline_without_rewriting_history():
    management = _al("codeunits/DHDeepScanMgt.Codeunit.al")
    runner = _al("codeunits/DHDeepScanRunner.Codeunit.al")
    client = _al("codeunits/DHApiClient.Codeunit.al")

    assert 'DeepScanRun."Scan Mode" := \'data_health_score\';' in management
    assert 'DeepScanRun."Headline" := CopyStr(GetHeadline(DeepScanRun, Score, IssuesCount)' in runner
    mapping = runner.split("local procedure GetHeadlineScanType", 1)[1].split(
        "local procedure GetRunningHeadline", 1
    )[0]
    assert "'data_health_score', 'free', 'free_deep':" in mapping
    assert "exit('free');" in mapping
    assert "'full', 'full_analysis', 'assessment':" in mapping
    assert "'monitoring', 'scheduled':" in mapping
    assert "exit('validation');" in mapping
    assert "ApplyAuthoritativeScanMode(DeepScanRun, GetJsonTokenText(Token));" in client
    assert "if (DeepScanRun.Status <> DeepScanRun.Status::Completed) or not IsGeneratedCompletionHeadline(DeepScanRun.\"Headline\") then" in client
    assert 'ScanHeader."Headline" := CopyStr(CorrectedHeadline' in client
