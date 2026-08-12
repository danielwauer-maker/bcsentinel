from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PERMISSION_FILE = ROOT / "bc-extension" / "app" / "src" / "permissionsets" / "BCSentinelPermissionSets.al"


def _source() -> str:
    return PERMISSION_FILE.read_text(encoding="utf-8")


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


def test_scan_user_cannot_modify_setup() -> None:
    block = _block("BCSENTINEL SCAN")
    assert 'tabledata "DH Setup" = R' in block
    assert 'tabledata "DH Setup" = RIMD' not in block
    assert 'codeunit "DH Scan Dispatcher" = X' in block
    assert 'codeunit "DH Deep Scan Runner" = X' in block


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
    assert re.search(r"\bpage\s+\"", block, flags=re.IGNORECASE) is None
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
