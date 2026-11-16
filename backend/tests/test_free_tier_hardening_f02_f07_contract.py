from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AL_ROOT = ROOT / "bc-extension" / "app" / "src"


def _al(relative_path: str) -> str:
    return (AL_ROOT / relative_path).read_text(encoding="utf-8-sig")


def test_full_or_monitoring_guard_requires_a_fresh_access_v2_capability():
    guard = _al("codeunits/DHAccessGuard.Codeunit.al")
    access_control = (ROOT / "backend/app/services/access_control_service.py").read_text(encoding="utf-8")

    method = guard.split("procedure EnsureFullOrMonitoringAccess()", 1)[1].split(
        "procedure HasFreshFullOrMonitoringAccess", 1
    )[0]
    assert "IsSnapshotFreshAndBound(Setup)" in method
    assert "TryRefreshAccessSnapshot(Setup)" in method
    assert "IsCapabilityGranted(Setup, 'monitoring_access')" in method
    assert "IsFullAssessmentGranted(Setup)" in method
    assert "IsCapabilityGranted(Setup, 'product_access')" in guard.split(
        "local procedure IsFullAssessmentGranted", 1
    )[1].split("local procedure HasFreshAssessmentProduct", 1)[0]
    assert "FullOrMonitoringRequiredErr" in method
    assert 'CAPABILITY_PRODUCT' in access_control
    assert 'CAPABILITY_MONITORING' in access_control
    api_client = _al("codeunits/DHApiClient.Codeunit.al")
    assert "JsonResponse.Get('product_model', ProductModelToken)" in api_client
    assert "JsonArrayContainsText(CommercialOffers, 'assessment')" in api_client


def test_free_cannot_open_or_mutate_dh_exceptions_through_pages_or_codeunits():
    exception_mgt = _al("codeunits/DHExceptionMgt.Codeunit.al")
    generic_remediation = _al("codeunits/DHGenericRemediation.Codeunit.al")
    exceptions_page = _al("pages/DHIssueExceptions.Page.al")
    dialog = _al("pages/DHExceptionDialog.Page.al")

    for procedure in (
        "OpenCustomerExceptions",
        "OpenVendorExceptions",
        "OpenItemExceptions",
        "DeactivateExceptionEntry",
        "ReactivateExceptionEntry",
    ):
        body = exception_mgt.split(f"procedure {procedure}", 1)[1].split("end;", 1)[0]
        assert "EnsureExceptionAccess();" in body
    assert "EnsureExceptionAccess();" in exception_mgt.split(
        "local procedure AddOrActivateException", 1
    )[1].split("local procedure RegisterAppliedException", 1)[0]
    assert "EnsureExceptionAccess();" in exception_mgt.split(
        "local procedure DeactivateException", 1
    )[1].split("local procedure EnsureExceptionAccess", 1)[0]
    assert "AccessGuard.EnsureFullOrMonitoringAccess();" in exception_mgt
    assert "AccessGuard.EnsureFullOrMonitoringAccess();" in generic_remediation.split(
        "local procedure EnsureExceptionAccess", 1
    )[1]
    assert "AccessGuard.EnsureFullOrMonitoringAccess();" in exceptions_page.split(
        "trigger OnOpenPage()", 1
    )[1].split("trigger OnAfterGetRecord", 1)[0]
    assert "AccessGuard.EnsureFullOrMonitoringAccess();" in dialog.split(
        "trigger OnOpenPage()", 1
    )[1].split("trigger OnQueryClosePage", 1)[0]


def test_free_cannot_change_modules_or_checks_but_full_and_monitoring_can():
    check_mgt = _al("codeunits/DHScanCheckMgt.Codeunit.al")
    checks_page = _al("pages/DHScanChecks.Page.al")
    modules_page = _al("pages/DHScanModules.Page.al")
    setup_page = _al("pages/DHSetup.Page.al")
    setup_table = _al("tables/DHSetup.Table.al")

    assert "AccessGuard.EnsureFullOrMonitoringAccess();" in check_mgt
    assert "AccessGuard.HasFreshFullOrMonitoringAccess()" in check_mgt
    for procedure in ("EnableAll", "DisableAll", "RestoreDefaults"):
        body = check_mgt.split(f"procedure {procedure}", 1)[1].split("end;", 1)[0]
        assert "EnsureSelectionAccess(false);" in body
    assert "Editable = CanEditSelection;" in checks_page
    assert "ScanCheckMgt.EnsureSelectionAccess(false);" in checks_page
    assert "Enabled = CanEditSelection;" in checks_page
    assert "ModifyAllowed = false;" not in checks_page
    on_open = checks_page.split("trigger OnOpenPage()", 1)[1].split(
        "trigger OnAfterGetRecord", 1
    )[0]
    assert "if CanEditSelection then" in on_open
    assert "EnsureSelectionAccess();" in modules_page
    assert modules_page.count("Enabled = CanEditSelection;") >= 3
    assert "ScanCheckMgt.HasSelectionAccess();" in modules_page
    assert "ScanCheckMgt.HasSelectionAccess();" in setup_page
    assert "AccessGuard.EnsureFullOrMonitoringAccess();" in setup_table.split(
        "procedure SetAllScanModules", 1
    )[1].split("procedure RestoreDefaultScanModules", 1)[0]
    assert "EnsureMonitoringAccess" not in checks_page
    assert "EnsureMonitoringAccess" not in modules_page
    assert "EnsureMonitoringAccess" not in setup_page


def test_full_and_monitoring_unlock_findings_and_free_copy_stays_limited():
    findings_list = _al("pages/DHDeepScanFindingsList.Page.al")
    findings_part = _al("pages/DHDeepScanFindings.Page.al")
    setup = _al("tables/DHSetup.Table.al")

    for source in (findings_list, findings_part):
        assert "AccessGuard.HasFreshFullOrMonitoringAccess()" in source
        assert (
            "Detailed data-quality issues, root causes, and recommended actions are included in Full Assessment. "
            "Start a Full Assessment to unlock this information."
        ) in source
        assert 'if Setup."Premium Enabled" then' not in source
    assert "Unlimited – Free" in setup
    assert "In development" in setup
    assert "Full Assessment required" in setup
    free_only = setup.split("local procedure HasExclusiveFreeAccess", 1)[1].split(
        "local procedure GetResultAccessDisplay", 1
    )[0]
    assert 'not "Premium Enabled" and not "Can Use Monitoring"' in free_only
