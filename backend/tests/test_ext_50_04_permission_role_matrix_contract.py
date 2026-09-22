from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PERMISSION_FILE = ROOT / "bc-extension" / "app" / "src" / "permissionsets" / "BCSentinelPermissionSets.al"
EVIDENCE_FILE = ROOT / "quality" / "release" / "ext-50-04-permission-role-matrix-evidence.json"
DOC_FILE = ROOT / "docs" / "EXT_50_04_PERMISSION_ROLE_MATRIX.md"
RUNTIME_CHECKLIST = ROOT / "docs" / "EXT_50_04_RUNTIME_NO_SUPER_CHECKLIST.md"
SCAN_DISPATCHER_FILE = ROOT / "bc-extension" / "app" / "src" / "codeunits" / "DHScanDispatcher.Codeunit.al"
API_CLIENT_FILE = ROOT / "bc-extension" / "app" / "src" / "codeunits" / "DHApiClient.Codeunit.al"


def _source() -> str:
    return PERMISSION_FILE.read_text(encoding="utf-8")


def _evidence() -> dict:
    return json.loads(EVIDENCE_FILE.read_text(encoding="utf-8"))


def _block(name: str) -> str:
    source = _source()
    match = re.search(
        rf'permissionset\s+\d+\s+"{re.escape(name)}"\s*\{{(?P<body>.*?)(?=\npermissionset\s+\d+\s+"|\Z)',
        source,
        flags=re.DOTALL | re.IGNORECASE,
    )
    assert match, f"Permission set {name} missing"
    return match.group("body")


def test_expected_assignable_roles_exist() -> None:
    for name in (
        "BCSENTINEL VIEWER",
        "BCSENTINEL SCAN",
        "BCSENTINEL SETUP",
        "BCSENTINEL ADMIN",
        "BCSENTINEL SCHEDULER",
    ):
        block = _block(name)
        assert "Assignable = true;" in block


def test_no_super_dependency_is_encoded() -> None:
    source = _source().upper()
    assert "SUPER" not in source


def test_viewer_is_read_only_on_bcsentinel_tables() -> None:
    block = _block("BCSENTINEL VIEWER")
    table_permissions = re.findall(r'tabledata\s+"[^"]+"\s*=\s*([RIMD]+)', block)
    assert table_permissions, "Viewer must expose BCSentinel data read permissions"
    assert set(table_permissions) == {"R"}, f"Viewer has write permissions: {table_permissions}"


def test_scan_user_cannot_modify_setup_directly() -> None:
    block = _block("BCSENTINEL SCAN")
    match = re.search(r'tabledata\s+"DH Setup"\s*=\s*([RIMD]+)', block)
    assert match, "SCAN role must declare DH Setup permission"
    assert match.group(1) == "R", f"SCAN role must keep DH Setup read-only, got {match.group(1)}"
    assert 'codeunit "DH Scan Dispatcher" = X' in block
    assert 'codeunit "DH Deep Scan Runner" = X' in block


def test_scan_runtime_writes_use_indirect_codeunit_permissions() -> None:
    dispatcher = SCAN_DISPATCHER_FILE.read_text(encoding="utf-8")
    api_client = API_CLIENT_FILE.read_text(encoding="utf-8")

    assert 'Permissions = tabledata "DH Setup" = RM;' in dispatcher
    assert 'Permissions = tabledata "DH Setup" = RM;' in api_client


def test_setup_role_can_configure_but_not_write_scan_results() -> None:
    block = _block("BCSENTINEL SETUP")
    assert 'tabledata "DH Setup" = RIMD' in block
    assert 'tabledata "DH Scan Check Selection" = RIMD' in block
    for result_table in (
        '"DH Scan Header"',
        '"DH Scan Issue"',
        '"DH Deep Scan Run"',
        '"DH Deep Scan Finding"',
        '"DH Dashboard Issue"',
    ):
        assert f"tabledata {result_table}" not in block


def test_scheduler_is_headless_and_setup_read_only() -> None:
    block = _block("BCSENTINEL SCHEDULER")
    assert 'tabledata "DH Setup" = R' in block
    assert re.search(r'\bpage\s+"', block, flags=re.IGNORECASE) is None
    assert 'codeunit "DH Scheduled Scan Runner" = X' in block
    assert 'codeunit "DH Scheduled Scan Failure" = X' in block


def test_admin_contains_full_bcsentinel_data_permissions() -> None:
    block = _block("BCSENTINEL ADMIN")
    for table_name in (
        "DH Setup",
        "DH Scan Header",
        "DH Scan Issue",
        "DH Deep Scan Run",
        "DH Deep Scan Finding",
        "DH Dashboard Issue",
        "DH Issue Exception",
        "DH Issue Action Log",
    ):
        assert f'tabledata "{table_name}" = RIMD' in block


def test_runtime_method_keeps_super_admin_as_untouched_recovery_anchor() -> None:
    evidence = _evidence()
    anchor = evidence["runtime_method"]["super_admin_anchor"]
    assert anchor == {
        "required": True,
        "remains_super": True,
        "used_for_no_super_evidence": False,
        "permission_changes_allowed_during_test": False,
    }


def test_runtime_method_allows_one_reusable_non_super_identity_with_strict_role_reset() -> None:
    evidence = _evidence()
    method = evidence["runtime_method"]
    assert method["strategy"] == "single_reusable_non_super_user_sequential_roles"
    assert method["separate_user_per_role_required"] is False
    assert method["dedicated_licensed_test_user_required"] is True
    assert method["test_identity"]["super"] is False

    transition = method["role_transition_requirements"]
    assert all(
        transition[key] is True
        for key in (
            "remove_all_bcsentinel_permission_sets_before_each_scenario",
            "preserve_documented_standard_bc_baseline",
            "assign_exactly_one_bcsentinel_role_except_plain_user_case",
            "verify_super_false",
            "capture_effective_permissions",
            "renew_user_session_after_permission_change",
            "record_expected_and_actual_result",
            "classify_unexpected_failure_before_code_change",
        )
    )


def test_runtime_evidence_preserves_no_super_isolation_while_progressing() -> None:
    evidence = _evidence()
    assert evidence["branch"].startswith("sprint/ext-50-04-runtime")
    assert evidence["status"] in {
        "AWAITING_MANUAL_BC_RUNTIME_EVIDENCE",
        "PARTIAL_RUNTIME_PASS__PLAIN_USER_DENIAL_VERIFIED",
        "PARTIAL_RUNTIME_PASS__PLAIN_USER_AND_VIEWER_CORE_VERIFIED",
        "FIX_IMPLEMENTED_AWAITING_1_0_2_23_RUNTIME_RETEST",
        "RUNTIME_PASS",
    }

    for role_name, role in evidence["roles"].items():
        assert role["super"] is False, role_name

    assert evidence["roles"]["plain_bc_user"]["permission_set"] == "NONE"
    assert evidence["runtime_method"]["standard_bc_baseline"]["super"] is False
    assert evidence["runtime_method"]["standard_bc_baseline"]["super_data"] is False
    assert evidence["runtime_method"]["standard_bc_baseline"]["security"] is False


def test_runtime_documentation_and_checklist_encode_safe_single_user_method() -> None:
    doc = DOC_FILE.read_text(encoding="utf-8")
    checklist = RUNTIME_CHECKLIST.read_text(encoding="utf-8")

    for expected in (
        "Recovery-Anker",
        "ein einzelner zusätzlicher, lizenzierter Testbenutzer",
        "SUPER = nein",
        "Effective Permissions",
        "BCSENTINEL_PERMISSION_GAP",
        "LICENSE_ENTITLEMENT_LIMIT",
    ):
        assert expected in doc

    for expected in (
        "SUPER-Admin bleibt unverändert",
        "Neutralzustand",
        "BCSENTINEL VIEWER",
        "BCSENTINEL SCAN",
        "BCSENTINEL SETUP",
        "BCSENTINEL SCHEDULER",
        "BCSENTINEL ADMIN",
        "Kein BCSentinel Permission Set",
    ):
        assert expected in checklist
