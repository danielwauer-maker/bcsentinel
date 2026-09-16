from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECOVERY = ROOT / "bc-extension/app/src/codeunits/DHCopiedCompanyRecovery.Codeunit.al"
PAGE_EXT = ROOT / "bc-extension/app/src/pageextensions/DHSetupCopiedCompanyRecovery.PageExt.al"
PERMISSION_EXT = ROOT / "bc-extension/app/src/permissionsets/BCSentinelCopiedCompanyRecovery.PermissionSetExt.al"
BACKEND_REG = ROOT / "backend/app/services/tenant_registration_service.py"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def test_recovery_is_local_only_and_never_force_rebinds_backend():
    source = text(RECOVERY)
    lowered = source.lower()
    assert "deleteapitoken" in lowered
    assert 'setup."tenant id" := \'\'' in lowered
    assert "registertenant" not in lowered
    assert "httpclient" not in lowered
    assert "force rebind" in lowered
    assert "backend call" in lowered


def test_identity_mismatch_uses_full_bc_identity_snapshot():
    source = text(RECOVERY)
    for field in (
        '"Access Snapshot Tenant ID"',
        '"Access Snapshot Environment"',
        '"Access Snapshot Env. Type"',
        '"Access Snapshot Company ID"',
    ):
        assert field in source
    for getter in ("GetEntraTenantId", "GetEnvironmentName", "GetEnvironmentType", "GetCompanyId"):
        assert getter in source
    assert "Legacy" in source and "Mismatch" in source and "Matched" in source


def test_recovery_does_not_touch_business_master_or_ledger_tables():
    source = text(RECOVERY)
    forbidden = (
        'Record Customer', 'Record Vendor', 'Record Item', 'Record "G/L Entry"',
        'Record "Customer Ledger Entry"', 'Record "Vendor Ledger Entry"',
        'Record "Item Ledger Entry"',
    )
    for token in forbidden:
        assert token not in source


def test_scheduler_is_detached_without_canceling_source_company_task():
    source = text(RECOVERY)
    assert 'Setup."Scheduled Scans Enabled" := false' in source
    assert 'Clear(Setup."Scheduled Scan Task ID")' in source
    assert "CancelTask(" not in source
    assert "DisableScheduler(" not in source


def test_cancel_is_non_destructive_and_default_is_no():
    source = text(RECOVERY)
    assert "Confirm(RecoveryConfirmQst, false)" in source
    assert "exit(false)" in source
    page = text(PAGE_EXT)
    assert "if not RecoveryMgt.RecoverCopiedCompany(Rec) then" in page
    assert "exit;" in page


def test_recovery_is_admin_only():
    page = text(PAGE_EXT)
    permissions = text(PERMISSION_EXT)
    assert 'AccessByPermission = codeunit "DH Copied Company Recovery" = X;' in page
    assert 'extends "BCSENTINEL ADMIN"' in permissions
    assert 'codeunit "DH Copied Company Recovery" = X;' in permissions


def test_backend_identity_guard_remains_strict():
    source = text(BACKEND_REG)
    assert "RegistrationConflictError" in source
    assert "Existing tenant is already bound to another Business Central identity." in source
    assert "tenant.registration_identity_key != identity.key" in source


def test_copied_bcsentinel_history_is_cleared_but_scan_configuration_is_not():
    source = text(RECOVERY)
    for table in (
        'Record "DH Scan Header"', 'Record "DH Deep Scan Run"', 'Record "DH Scan Trend"',
        'Record "DH Dashboard Issue"', 'Record "DH Issue Exception"',
        'Record "DH Issue Action Log"', 'Record "DH Duplicate Buffer"',
    ):
        assert table in source
    assert 'Record "DH Scan Check Selection"' not in source
    assert 'Setup."Scan System Module"' not in source


def test_access_and_registration_state_are_fail_closed_after_recovery():
    source = text(RECOVERY)
    expected = (
        'Setup.Registered := false', 'Setup."Premium Enabled" := false',
        'Setup."Monitoring Active" := false', 'Setup."Can Run Deep Scan" := false',
        'Setup."Can View Dashboard" := false', 'Setup."Can View Issue Details" := false',
        'Setup."Can View Reports" := false', 'Setup."Can Use Monitoring" := false',
        'Setup."Subscription Active" := false', 'Setup.InvalidateAccessSnapshot()',
    )
    for token in expected:
        assert token in source
