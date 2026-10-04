#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "quality" / "s07" / "legacy-pr-catalog.json"
TRACE = ROOT / "quality" / "s07" / "legacy-canonical-traceability.json"
STRUCTURE = ROOT / "config" / "canonical-repository.yaml"

catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
trace = json.loads(TRACE.read_text(encoding="utf-8"))
structure = yaml.safe_load(STRUCTURE.read_text(encoding="utf-8"))

prs = catalog["pull_requests"]
numbers = [item["number"] for item in prs]
if len(numbers) != len(set(numbers)):
    raise SystemExit("Duplicate pull request number in S07 catalog")
if min(numbers) != 1 or max(numbers) < 52:
    raise SystemExit("S07 PR catalog does not cover the known repository history through PR #52")
if catalog["github_releases_observed"] != 0:
    raise SystemExit("Update S07 release policy when formal GitHub Releases are introduced")

for zone in structure["canonical_zones"].values():
    for path in zone["paths"]:
        if not (ROOT / path).exists():
            raise SystemExit(f"Canonical repository path missing: {path}")

legacy_paths = {item["path"] for item in structure["legacy_or_transition_zones"]}
for required in {"landingpage", "go-live-readiness-2026", "output"}:
    if required not in legacy_paths:
        raise SystemExit(f"Missing legacy-zone mapping: {required}")

for mapping in trace["mappings"]:
    if mapping["status"] != "mapped":
        raise SystemExit(f"Unclosed traceability mapping: {mapping['legacy']}")

print("S07 canonical repository governance: PASS")
