#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "config" / "e8-release-candidate-freeze.json").read_text(encoding="utf-8"))
builder = (ROOT / "scripts" / "build_e8_release_manifest.py").read_text(encoding="utf-8")
deploy = (ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")

if contract.get("official_sprint_done") is not False:
    raise SystemExit("E8 automation must not claim official E8 completion.")
if contract.get("official_go_live_readiness_owned_here") is not False:
    raise SystemExit("E8 automation must not own official Go-Live readiness.")

for relative in contract["required_evidence_contracts"]:
    if not (ROOT / relative).exists():
        raise SystemExit(f"E8 evidence contract missing: {relative}")

for needle in (
    'bc-extension/app.json',
    'dashboard/package.json',
    '["alembic", "heads"]',
    'full immutable 40-character Git SHA',
    'x8.get("pre_manual_ready") is not True',
    '"official_e8_done": False',
    '"release_ref": sha',
):
    if needle not in builder:
        raise SystemExit(f"E8 manifest builder evidence missing: {needle}")

for needle in (
    "workflow_dispatch:",
    "release_ref:",
    "PROMOTE_TO_PROD",
    "git checkout --detach \"$RELEASE_REF\"",
):
    if needle not in deploy:
        raise SystemExit(f"E8 deployment freeze boundary missing: {needle}")
if "branches:\n      - main" in deploy:
    raise SystemExit("E8 forbids automatic main-to-PROD deployment.")

rules = contract.get("freeze_rules", {})
if not all(rules.values()):
    raise SystemExit("E8 freeze rules must remain explicit and enabled.")
manual = contract.get("manual_evidence_required", [])
for required in ("E3", "E4", "E5", "E6", "E7", "Final visual", "Explicit human"):
    if not any(item.startswith(required) for item in manual):
        raise SystemExit(f"E8 must retain manual evidence requirement: {required}")

print("E8 Release Candidate Freeze automation contract: PASS")
print("Official E8 remains open pending consolidated manual/external evidence and human authorization.")
