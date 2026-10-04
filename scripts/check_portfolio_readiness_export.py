#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "quality" / "portfolio-readiness-evidence.json"

payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
facts = payload["facts"]
rendered_facts = json.dumps(facts).lower()

if "percentage" in rendered_facts or "readiness_pct" in rendered_facts:
    raise SystemExit("Portfolio evidence export must not contain calculated percentages.")
if not all("complete" in fact for fact in facts.values()):
    raise SystemExit("Every exported fact must expose an explicit complete boolean.")
print("portfolio readiness export contract: PASS")
