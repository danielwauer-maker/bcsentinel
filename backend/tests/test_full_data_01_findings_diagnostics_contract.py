from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AL_ROOT = ROOT / "bc-extension" / "app" / "src"


def _al(relative_path: str) -> str:
    return (AL_ROOT / relative_path).read_text(encoding="utf-8-sig")


def test_sandbox_findings_diagnostics_is_read_only_and_run_scoped():
    diagnostics = _al("codeunits/DHFindingsDiagnosticsMgt.Codeunit.al")
    setup = _al("pages/DHSetup.Page.al")
    permissions = _al("permissionsets/BCSentinelPermissionSets.al")

    assert 'codeunit 53348 "DH Findings Diagnostics Mgt."' in diagnostics
    assert "IdentityMgt.GetEnvironmentType() <> 'sandbox'" in diagnostics
    assert 'DeepScanRun.SetRange(Status, DeepScanRun.Status::Completed);' in diagnostics
    assert 'Finding.SetRange("Deep Scan Entry No.", DeepScanRun."Entry No.");' in diagnostics
    assert 'PageFilteredFinding.SetRange("Deep Scan Entry No.", DeepScanRun."Entry No.");' in diagnostics
    assert "AccessGuard.HasFreshFullOrMonitoringAccess()" in diagnostics
    assert "Insert(" not in diagnostics
    assert "Modify(" not in diagnostics
    assert "Delete" not in diagnostics
    assert "DH Findings Diagnostics Mgt." in setup
    assert "DH Findings Diagnostics Mgt." in permissions
