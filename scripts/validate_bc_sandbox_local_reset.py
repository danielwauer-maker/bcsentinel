#!/usr/bin/env python3
"""Static regression contract for the sandbox-only local BCSentinel reset."""

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "bc-extension"
RESET = APP / "app/src/codeunits/DHSandboxResetMgt.Codeunit.al"
SETUP = APP / "app/src/tables/DHSetup.Table.al"
PAGE = APP / "app/src/pages/DHSetup.Page.al"
PERMISSIONS = APP / "app/src/permissionsets/BCSentinelPermissionSets.al"

REQUIRED_DELETES = (
    "NotificationDelivery", "NotificationEvent", "NotificationConfigAudit",
    "NotificationRecipient", "NotificationRule", "NotificationTemplate",
    "NotificationSetup", "RemediationAudit", "RemediationAction",
    "IssueActionLog", "IssueException", "DeepScanFinding", "ScanIssue",
    "DashboardIssue", "DeepScanRun", "ScanHeader", "ScanTrend",
    "DuplicateBuffer", "ScanCheckSelection",
)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    manifest = json.loads((APP / "app.json").read_text(encoding="utf-8-sig"))
    cloud_manifest = json.loads((APP / "app.cloud.json").read_text(encoding="utf-8-sig"))
    reset = RESET.read_text(encoding="utf-8-sig")
    setup = SETUP.read_text(encoding="utf-8-sig")
    page = PAGE.read_text(encoding="utf-8-sig")
    permissions = PERMISSIONS.read_text(encoding="utf-8-sig")

    require(manifest["version"] == "1.0.2.61", "app.json must be 1.0.2.61", errors)
    require(cloud_manifest["version"] == "1.0.2.61", "app.cloud.json must be 1.0.2.61", errors)
    require("EnvironmentInfo.IsSandbox()" in reset, "server-side sandbox guard is missing", errors)
    require("EnsureNoActiveScan();" in reset, "active-scan guard is missing", errors)
    require("EnsureNoUnmanagedScheduledTask(Setup);" in reset, "scheduler-task guard is missing", errors)
    require("DH API Client" not in reset, "reset must not call a backend cleanup API", errors)
    require("SecretMgt.DeleteApiToken(Setup);" in reset, "isolated-storage token deletion is missing", errors)
    require("Setup.ClearSandboxRegistrationState();" in reset, "registration/snapshot invalidation is missing", errors)
    for record in REQUIRED_DELETES:
        require(f"{record}.DeleteAll(false);" in reset, f"local {record} purge is missing", errors)

    action_start = page.find("action(ResetSandboxBCSentinelData)")
    action_end = page.find("            action(RequestAccess)", action_start)
    action = page[action_start:action_end] if action_start >= 0 and action_end >= 0 else ""
    require(action.count("Confirm(") == 2, "two explicit UI confirmations are required", errors)
    require('AccessByPermission = Codeunit "DH Sandbox Reset Mgt." = X;' in page,
            "reset action must be restricted to BCSentinel Admin", errors)
    require("procedure ClearSandboxRegistrationState()" in setup,
            "defined unregistered reset state is missing", errors)
    for field in ("Tenant ID", "Access Snapshot Tenant ID", "Free Assessment Used", "Monitoring Until"):
        require(field in setup, f"setup reset must address {field}", errors)
    require('codeunit "DH Sandbox Reset Mgt." = X' in permissions,
            "BCSENTINEL ADMIN must execute the reset manager", errors)

    if errors:
        print("BC sandbox local reset contract: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("BC sandbox local reset contract: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
