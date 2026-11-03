#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "bc-extension" / "app.json"
PERMISSIONS = ROOT / "bc-extension" / "app" / "src" / "permissionsets" / "BCSentinelPermissionSets.al"
PILOT_PERMISSION = ROOT / "bc-extension" / "app" / "src" / "permissionsets" / "BCSentinelPilot.PermissionSet.al"
SETUP_PAGE = ROOT / "bc-extension" / "app" / "src" / "pages" / "DHSetup.Page.al"


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    app = json.loads(APP.read_text(encoding="utf-8-sig"))
    version = tuple(int(x) for x in str(app.get("version", "0")).split("."))

    require(version >= (1, 0, 2, 30), "Extension version must be >= 1.0.2.30 for the controlled pilot candidate.", errors)
    require(app.get("runtime") == "16.0", "Controlled pilot runtime must remain 16.0.", errors)
    require(str(app.get("application", "")).startswith("27."), "Application target must remain BC 27.x.", errors)
    require(str(app.get("platform", "")).startswith("27."), "Platform target must remain BC 27.x.", errors)
    require(app.get("privacyStatement") == "https://bcsentinel.com/datenschutz", "Manifest privacyStatement must use the canonical /datenschutz route.", errors)
    require(app.get("url") == "https://bcsentinel.com", "Manifest product URL must be canonical.", errors)

    permissions = PERMISSIONS.read_text(encoding="utf-8-sig")
    pilot = PILOT_PERMISSION.read_text(encoding="utf-8-sig")
    setup = SETUP_PAGE.read_text(encoding="utf-8-sig")

    for permission_set in ("BCSENTINEL VIEWER", "BCSENTINEL SCAN", "BCSENTINEL SETUP", "BCSENTINEL ADMIN"):
        require(permission_set in permissions, f"Missing permission set {permission_set}.", errors)

    for included in ("BCSENTINEL SETUP", "BCSENTINEL SCAN", "BCSENTINEL VIEWER"):
        require(included in pilot, f"BCSENTINEL PILOT must include {included}.", errors)

    for action in ("RegisterTenant", "TestConnection", "RefreshLicenseStatus", "StartScan", "ViewScanHistory"):
        require(f"action({action})" in setup, f"Setup page is missing required pilot action {action}.", errors)

    require('field("Data Processing Consent"' in setup, "Setup page must expose Data Processing Consent.", errors)
    require('field("Registration Invite Code"' in setup, "Setup page must expose the controlled-pilot invite code.", errors)
    require('field("Tenant ID"' in setup and "Visible = false;" in setup, "Internal Tenant ID must remain hidden from normal customer setup.", errors)

    if errors:
        print("Controlled pilot Extension static readiness: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Controlled pilot Extension static readiness: PASS (version {app['version']})")
    print("Manual evidence still required: AL compile/package, real BC Online install/upgrade, non-SUPER runtime, scan/report journey.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
