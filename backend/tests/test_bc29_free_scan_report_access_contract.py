from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AL_ROOT = ROOT / "bc-extension" / "app" / "src"


def _al(relative_path: str) -> str:
    return (AL_ROOT / relative_path).read_text(encoding="utf-8-sig")


def test_completed_headline_uses_the_persisted_scan_mode_for_all_product_families():
    runner = _al("codeunits/DHDeepScanRunner.Codeunit.al")

    assert 'GetHeadline(DeepScanRun, Score, IssuesCount)' in runner
    assert 'local procedure GetHeadline(var DeepScanRun: Record "DH Deep Scan Run"; Score: Integer; IssuesCount: Integer): Text' in runner
    assert 'local procedure GetHeadlineScanType(var DeepScanRun: Record "DH Deep Scan Run"): Text' in runner
    for scan_type, completed_label in (
        ("'free'", "GetFreeScanHeadline(Score, IssuesCount)"),
        ("'full'", "GetFullAssessmentHeadline(Score, IssuesCount)"),
        ("'monitoring'", "GetMonitoringScanHeadline(Score, IssuesCount)"),
    ):
        assert scan_type in runner
        assert completed_label in runner
    assert "GetValidationCheckHeadline(Score, IssuesCount)" in runner
    assert "Free Scan completed with critical findings." in runner
    assert "Full Assessment completed with critical findings." in runner
    assert "Monitoring Scan completed with critical findings." in runner
    assert "Validation Check completed with critical findings." in runner


def test_free_scan_is_routed_only_to_the_scoped_free_live_grant():
    links = _al("codeunits/DHReportLinkMgt.Codeunit.al")
    setup_page = _al("pages/DHSetup.Page.al")
    monitor = _al("pages/DHDeepScanMonitor.Page.al")
    history = _al("pages/DHDeepScanRuns.Page.al")

    report_variant = links.split("procedure GetCompletedReportVariant", 1)[1].split(
        "local procedure GetReportErrorText", 1
    )[0]
    assert "'data_health_score', 'free', 'free_deep':\n                exit('free');" in report_variant
    assert "'full', 'full_analysis', 'assessment':\n                exit('full');" in report_variant

    free_link = links.split("procedure OpenFreeHealthReport", 1)[1].split(
        "procedure ReviewScopeAndOpenFullV6", 1
    )[0]
    assert "'/reports/live/free/' + Format(ScanId) + '/link'" in free_link
    assert "'/reports/free-health/'" not in free_link
    assert "Content.WriteFrom('{}');" in free_link
    assert "if not Client.Post(Url, Content, Response) then" in free_link
    assert "X-Tenant-Id" in free_link
    assert "X-Api-Token" in free_link
    assert "OpenArchivedFullV6" not in free_link

    for source in (setup_page, monitor, history):
        assert "OpenFreeHealthReport" in source
    assert "ShowFreeReport" in monitor
    assert "ShowFreeReport" in history
    assert "'free':\n                ReportLinks.OpenFreeHealthReport(DeepScanRun.\"Run ID\");" in setup_page


def test_full_report_route_and_access_v2_free_guard_remain_separate():
    links = _al("codeunits/DHReportLinkMgt.Codeunit.al")
    free_reports = (ROOT / "backend" / "app" / "routers" / "report_legacy_family.py").read_text(encoding="utf-8")
    archive = (ROOT / "backend" / "app" / "services" / "report_archive_service.py").read_text(encoding="utf-8")

    full_link = links.split("procedure OpenArchivedFullV6", 1)[1].split(
        "procedure OpenFreeHealthReport", 1
    )[0]
    assert "'/reports/executive/' + Format(ScanId) + '/v6-link'" in full_link
    assert "'/reports/free-health/'" not in full_link
    assert "if (Variant <> 'validation') and (Variant <> 'monitoring') then" in links
    assert "@router.post(\"/free-health/{scan_id}/share-link\"" in free_reports
    assert "not is_original_free_scan(db, tenant.tenant_id, scan_id)" in free_reports
    assert "if not has_paid_full_access(db, tenant):" in archive
    assert 'HTTPException(status_code=402, detail="FULL_ACCESS_INACTIVE")' in archive
