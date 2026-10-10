#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "config" / "x1-ui-convergence.json").read_text(encoding="utf-8"))
styles = (ROOT / "dashboard" / "src" / "styles.css").read_text(encoding="utf-8")
shell = (ROOT / "dashboard" / "src" / "foundation" / "AppShell.tsx").read_text(encoding="utf-8")
contexts = (ROOT / "dashboard" / "src" / "foundation" / "contexts.tsx").read_text(encoding="utf-8")
client = (ROOT / "dashboard" / "src" / "api" / "client.ts").read_text(encoding="utf-8")
main = (ROOT / "dashboard" / "src" / "main.tsx").read_text(encoding="utf-8")

required_css = {
    "brand_orange": "--brand-orange: #FF921F",
    "brand_orange_foreground": "--on-brand-orange: #082138",
    "interaction_primary": "--interaction-primary: #246BFD",
    "navigation": "--navigation: #14213D",
    "page": "--page: #F7F9FC",
    "card": "--card: #FFFFFF",
    "success": "--success: #11A36A",
    "warning": "--warning: #D98E04",
    "critical": "--critical: #CF3A3A",
}
for key, needle in required_css.items():
    if needle not in styles:
        raise SystemExit(f"X1 token mismatch: {key} missing from dashboard CSS")

if "font-family: Inter" not in styles:
    raise SystemExit("X1 typography mismatch: Inter is not the dashboard baseline")
if ".button-brand { background: var(--brand-orange); color: var(--on-brand-orange); }" not in styles:
    raise SystemExit("X1 accessibility rule missing: brand CTA must use on-brand-orange foreground")

for item in contract["frozen_navigation"]:
    for value in (item["route"], item["de"], item["en"]):
        if value not in shell:
            raise SystemExit(f"X1 navigation mismatch: {value!r} missing from AppShell")

for required in (
    "useTenantSwitcher",
    "tenant-select",
    "tenantSummary.current_plan",
    "tenantSummary.role",
    "key={tenant?.tenantId}",
):
    if required not in shell:
        raise SystemExit(f"X1 tenant-switch UI contract missing: {required}")

for required in (
    "listAccountTenants",
    "createTenantSession",
    "accountSessionToken",
    "setTenant",
):
    if required not in contexts:
        raise SystemExit(f"X1 tenant-switch state contract missing: {required}")

for endpoint in ("/auth/account/tenants", "/auth/account/tenant-session"):
    if endpoint not in client:
        raise SystemExit(f"X1 account API contract missing: {endpoint}")

if "./x1.css" not in main:
    raise SystemExit("X1 shell convergence styles are not loaded")

print("X1 UI convergence contract: PASS")
