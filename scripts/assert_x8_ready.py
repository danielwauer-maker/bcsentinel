#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
audit = json.loads((ROOT / "config" / "x8-pre-manual-pilot-audit.json").read_text(encoding="utf-8"))

blockers = audit.get("code_blockers", [])
if blockers:
    details = ", ".join(f"{item.get('id')}[{item.get('severity')}]" for item in blockers)
    raise SystemExit(f"X8 NOT READY: unresolved code blockers: {details}")
if audit.get("status") != "ready":
    raise SystemExit(f"X8 NOT READY: audit status is {audit.get('status')!r}, expected 'ready'.")

print("X8 READY: no unresolved P0/P1 code blockers remain before manual acceptance.")
