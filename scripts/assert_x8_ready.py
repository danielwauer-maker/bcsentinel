#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
audit = json.loads((ROOT / "config" / "x8-pre-manual-pilot-audit.json").read_text(encoding="utf-8"))

if audit.get("pre_manual_ready") is not True or audit.get("status") != "ready":
    raise SystemExit("X8 pre-manual readiness is not asserted.")
if audit.get("code_blockers"):
    ids = ", ".join(item.get("id", "unknown") for item in audit["code_blockers"])
    raise SystemExit(f"X8 has unresolved code blockers: {ids}")
if audit.get("official_sprint_done") is not False:
    raise SystemExit("X8 readiness assertion must not claim official E8 completion.")

print("X8 pre-manual readiness assertion: PASS")
print("No known P0 product/code blockers remain.")
print("Manual/external acceptance remains mandatory before official readiness can advance.")
