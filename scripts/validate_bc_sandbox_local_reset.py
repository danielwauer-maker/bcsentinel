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
RECOVERY = APP / "app/src/codeunits/DHCopiedCompanyRecovery.Codeunit.al"

REQUIRED_DELETES = (
    "NotificationDelivery", "NotificationEvent", "NotificationConfigAudit",
    "NotificationRecipient", "NotificationRule", "NotificationTemplate",
    "NotificationSetup", "RemediationAudit", "RemediationAction",
    "IssueActionLog", "IssueException", "DeepScanFinding", "ScanIssue",
    "DashboardIssue", "DeepScanRun", "ScanHeader", "ScanTrend", "CheckExecution",
    "ScanRecordEvidence",
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
    scheduler = (APP / "app/src/codeunits/DHScanSchedulerMgt.Codeunit.al").read_text(encoding="utf-8-sig")
    recovery = RECOVERY.read_text(encoding="utf-8-sig")

    require(manifest["version"] == "1.0.2.61", "app.json must be 1.0.2.61", errors)
    require(cloud_manifest["version"] == "1.0.2.61", "app.cloud.json must be 1.0.2.61", errors)
    require("EnvironmentInfo.IsSandbox()" in reset, "server-side sandbox guard is missing", errors)
    require("EnsureNoActiveScan();" in reset, "active-scan guard is missing", errors)
    require("SchedulerMgt.StopSchedulerForSandboxReset(Setup);" in reset,
            "verified scheduler-stop guard is missing", errors)
    require(reset.count("EnsureNoActiveScan();") == 2,
            "reset must check active scans before and after scheduler cancellation", errors)
    require("DH API Client" not in reset, "reset must not call a backend cleanup API", errors)
    require("SecretMgt.DeleteApiToken(Setup);" in reset, "isolated-storage token deletion is missing", errors)
    require("Setup.ClearSandboxRegistrationState();" in reset, "registration/snapshot invalidation is missing", errors)
    for record in REQUIRED_DELETES:
        require(f"{record}.DeleteAll(false);" in reset, f"local {record} purge is missing", errors)

    action_start = page.find("action(ResetSandboxBCSentinelData)")
    action_end = page.find("            group(SubscriptionActions)", action_start)
    action = page[action_start:action_end] if action_start >= 0 and action_end >= 0 else ""
    require(action.count("Confirm(") == 2, "two explicit UI confirmations are required", errors)
    require('AccessByPermission = Codeunit "DH Sandbox Reset Mgt." = X;' in page,
            "reset action must be restricted to BCSentinel Admin", errors)
    require("procedure ClearSandboxRegistrationState()" in setup,
            "defined unregistered reset state is missing", errors)
    for field in ("Tenant ID", "Access Snapshot Tenant ID", "Free Assessment Used", "Monitoring Until"):
        require(field in setup, f"setup reset must address {field}", errors)
    admin_start = permissions.find('permissionset 53193 "BCSENTINEL ADMIN"')
    admin_end = permissions.find("permissionset ", admin_start + 1)
    admin_permissions = permissions[admin_start:admin_end] if admin_start >= 0 and admin_end >= 0 else ""
    require('codeunit "DH Sandbox Reset Mgt." = X' in admin_permissions,
            "BCSENTINEL ADMIN must execute the reset manager", errors)
    require("procedure StopSchedulerForSandboxReset(var Setup: Record \"DH Setup\")" in scheduler,
            "scheduler manager must expose the reset-specific stop operation", errors)
    require("if not TryCancelSchedulerTask(Setup.\"Scheduled Scan Task ID\") then" in scheduler,
            "scheduler reset stop must fail when task cancellation is not confirmed", errors)

    reset_state = setup.split("procedure ClearSandboxRegistrationState()", 1)[1].split("    procedure ", 1)[0]
    invalidate = setup.split("procedure InvalidateAccessSnapshot()", 1)[1].split("    procedure ", 1)[0]
    recovery_state = recovery.split("local procedure ResetCopiedRegistrationState", 1)[1].split("    begin", 1)[1].split("    end;", 1)[0]
    recovery_fields = set(__import__("re").findall(r'"([^"]+)"', recovery_state))
    state_fields = set(__import__("re").findall(r'"([^"]+)"', reset_state + invalidate))
    missing_parity = sorted(recovery_fields - state_fields)
    require(not missing_parity,
            "sandbox reset is missing copied-company registration fields: " + ", ".join(missing_parity), errors)
    for field in ("Premium Enabled", "Monitoring Active", "Can Run Deep Scan", "Can View Dashboard",
                  "Can View Issue Details", "Can View Reports", "Can Use Monitoring", "Subscription Active",
                  "Dashboard Access Until", "Issue Access Until", "Report Access Until", "Premium Until",
                  "Monitoring Until", "Free Assessment Used"):
        require(field in state_fields, f"sandbox reset must clear {field}", errors)

    if errors:
        print("BC sandbox local reset contract: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("BC sandbox local reset contract: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
