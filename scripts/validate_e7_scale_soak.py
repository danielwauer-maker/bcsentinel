#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "config" / "e7-scale-soak.json").read_text(encoding="utf-8"))
test_file = (ROOT / "backend" / "tests" / "test_e7_scale_multitenant.py").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "scale-soak-quality.yml").read_text(encoding="utf-8")

if contract.get("official_sprint_done") is not False:
    raise SystemExit("E7 automation must not claim official completion before real soak evidence.")
if contract.get("ci_scale_matrix") != [1, 5, 10, 25, 50]:
    raise SystemExit("E7 CI scale matrix drifted from the approved 1/5/10/25/50 tenant profile.")

for needle in (
    '@pytest.mark.parametrize("tenant_count", [1, 5, 10, 25, 50])',
    "/auth/account/session",
    "/auth/account/tenants",
    "/auth/account/tenant-session",
    "first_status_after_switches",
    "mixed.status_code == 403",
):
    if needle not in test_file:
        raise SystemExit(f"E7 scale evidence missing: {needle}")

for needle in (
    "test_e7_scale_multitenant.py",
    "test_x0_account_auth_switching.py",
    "test_e1_tenant_security.py",
):
    if needle not in workflow:
        raise SystemExit(f"E7 CI gate missing: {needle}")

soak = contract.get("soak_preparation", {})
if soak.get("duration_hours_target") != 24 or soak.get("tenant_count_target") != 50:
    raise SystemExit("E7 real soak target must remain 24h / 50 tenants.")
manual = contract.get("manual_evidence_required", [])
if not any("24-hour soak" in item for item in manual):
    raise SystemExit("E7 must retain a real 24-hour soak acceptance requirement.")

print("E7 Scale/Soak Preparation contract: PASS")
print("Official E7 remains open pending real 24-hour infrastructure soak evidence.")
