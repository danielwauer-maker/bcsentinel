#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "config" / "e6-synthetic-pilot-journey.json").read_text(encoding="utf-8"))
test_file = (ROOT / "backend" / "tests" / "test_e6_synthetic_pilot_journey.py").read_text(encoding="utf-8")

if contract.get("official_sprint_done") is not False:
    raise SystemExit("E6 synthetic automation must not claim official pilot completion.")

for needle in (
    "/public/pilot-interest",
    "/auth/account/session",
    "/auth/account/tenant-session",
    "/auth/account/tenants",
    "/analytics/get-token",
    "/analytics/embed/data",
    "/reports/executive/scan_e6_monitoring",
    "/reports/monitoring/scan_e6_monitoring",
    "foreign.status_code == 404",
    "wrong_header.status_code == 403",
):
    if needle not in test_file:
        raise SystemExit(f"E6 synthetic journey evidence missing: {needle}")

required = contract.get("required_boundaries", {})
if not all(required.values()):
    raise SystemExit("E6 required isolation/product boundaries must all be true.")

manual = contract.get("manual_evidence_required", [])
if not any("real Business Central" in item for item in manual):
    raise SystemExit("E6 must retain real Business Central pilot evidence.")

print("E6 Synthetic Pilot Journey contract: PASS")
print("Official E6 remains open pending the real controlled-pilot journey.")
