"""Regression gate for BC SaaS PTE0004 missing table permissions.

1.0.2.53 was rejected by the SaaS upload validator even though AL compiled.
Every persisted extension table must have a matching tabledata entry in an
assignable permission set. Historical permission-set object IDs stay stable.
"""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "bc-extension" / "app" / "src"
PERMISSIONS = SOURCE / "permissionsets" / "BCSentinelPermissionSets.al"

REQUIRED_TABLES = {
    "DH Notification Config Audit",
    "DH Notification Delivery",
    "DH Notification Event",
    "DH Notification Recipient",
    "DH Notification Rule",
    "DH Notification Setup",
    "DH Notification Template",
    "DH Remediation Action",
    "DH Remediation Audit",
}
EXPECTED_PERMISSION_SET_IDS = {
    "BCSENTINEL VIEWER": 53190,
    "BCSENTINEL SCAN": 53191,
    "BCSENTINEL SETUP": 53192,
    "BCSENTINEL ADMIN": 53193,
    "BCSENTINEL SCHEDULER": 53345,
}


def _permission_source() -> str:
    return PERMISSIONS.read_text(encoding="utf-8-sig")


def test_all_nine_saas_rejected_tables_have_explicit_permissions() -> None:
    text = _permission_source()
    for name in REQUIRED_TABLES:
        assert re.search(r'\btabledata\s+"' + re.escape(name) + r'"\s*=\s*[RIMD]+\s*[,;]', text), name


def test_setup_scan_admin_role_permissions_preserve_original_152_rights() -> None:
    text = _permission_source()
    for role in ("BCSENTINEL SCAN", "BCSENTINEL SETUP", "BCSENTINEL ADMIN"):
        role_match = re.search(
            r'permissionset\s+\d+\s+"' + re.escape(role) + r'"\s*\{(.*?)(?=\npermissionset\s+\d+|\Z)',
            text, flags=re.S,
        )
        assert role_match, role
        body = role_match.group(1)
        for name in REQUIRED_TABLES:
            assert re.search(r'\btabledata\s+"' + re.escape(name) + r'"\s*=\s*[RIMD]+\s*[,;]', body), (role, name)


def test_persisted_permission_set_object_ids_remain_unchanged() -> None:
    text = _permission_source()
    for name, expected_id in EXPECTED_PERMISSION_SET_IDS.items():
        assert re.search(r'\bpermissionset\s+' + str(expected_id) + r'\s+"' + re.escape(name) + r'"', text), name


def test_all_original_app_tables_have_matching_tabledata_permission() -> None:
    # This is an intentionally conservative source-level preflight, not a
    # substitute for Microsoft's SaaS PTECop validation during upload.
    perms = _permission_source()
    names = set()
    for file in (SOURCE / "tables").glob("*.al"):
        contents = file.read_text(encoding="utf-8-sig")
        match = re.search(r'^\s*table\s+\d+\s+"([^"]+)"', contents, re.M)
        if match:
            names.add(match.group(1))
    for name in sorted(names):
        assert re.search(r'\btabledata\s+"' + re.escape(name) + r'"\s*=\s*[RIMD]+\s*[,;]', perms), name
