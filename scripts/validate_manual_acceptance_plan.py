#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "config" / "manual-acceptance-plan.json"
data = json.loads(PLAN.read_text(encoding="utf-8"))

if data.get("contract") != "bcsentinel-manual-acceptance-v1":
    raise SystemExit("Unexpected manual acceptance contract.")
if data.get("official_readiness_owned_here") is not False:
    raise SystemExit("Manual acceptance plan must not own the official readiness KPI.")
if data.get("status") != "prepared":
    raise SystemExit("Manual acceptance plan must remain prepared until real evidence is recorded.")

required_gates = ["E3", "E4", "E5", "E6", "E7", "E8", "F1"]
if data.get("execution_order") != required_gates:
    raise SystemExit("Manual acceptance execution order drifted.")

allowed_results = set(data.get("result_enum", []))
if allowed_results != {"PENDING", "PASS", "FAIL", "BLOCKED"}:
    raise SystemExit("Manual acceptance result enum drifted.")

tests = data.get("tests") or []
if not tests:
    raise SystemExit("Manual acceptance plan contains no tests.")

ids = [item.get("id") for item in tests]
if len(ids) != len(set(ids)):
    raise SystemExit("Manual acceptance test IDs must be unique.")

counts = Counter(item.get("gate") for item in tests)
for gate in required_gates:
    if counts[gate] < 1:
        raise SystemExit(f"Manual acceptance gate has no tests: {gate}")

required_fields = {"id", "gate", "area", "actor", "surface", "action", "expected", "evidence", "result"}
for item in tests:
    missing = sorted(required_fields - set(item))
    if missing:
        raise SystemExit(f"{item.get('id')} missing fields: {missing}")
    if item["gate"] not in required_gates:
        raise SystemExit(f"{item['id']} has unsupported gate {item['gate']}")
    if item["result"] != "PENDING":
        raise SystemExit(f"Prepared matrix must not pre-claim acceptance: {item['id']}={item['result']}")
    if not isinstance(item["evidence"], list) or not item["evidence"]:
        raise SystemExit(f"{item['id']} requires explicit evidence.")
    for field in ("actor", "surface"):
        if not isinstance(item[field], str) or len(item[field].strip()) < 3:
            raise SystemExit(f"{item['id']} has incomplete {field} guidance.")
    for field in ("action", "expected"):
        if not isinstance(item[field], str) or len(item[field].strip()) < 8:
            raise SystemExit(f"{item['id']} has incomplete {field} guidance.")

required_test_ids = {
    "E3-ROLE-VIEWER",
    "E3-ROLE-SCAN",
    "E3-ROLE-SETUP",
    "E3-ROLE-SCHEDULER",
    "E3-ROLE-ADMIN",
    "E3-SCAN-FLOW",
    "E3-EXCEPTION-SNAPSHOT",
    "E3-NOTIFICATION-RUNTIME",
    "E4-STRIPE-LIST-PRICE",
    "E4-STRIPE-TENANT-OVERRIDE",
    "E4-STRIPE-PROMOTION",
    "E4-SPONSORED-PILOT",
    "E4-STRIPE-LIFECYCLE",
    "E4-EMAIL-DELIVERY-DE",
    "E4-EMAIL-DELIVERY-EN",
    "E4-DNS-MAIL-AUTH",
    "E5-OFFHOST-RESTORE",
    "E5-RTO-RPO",
    "E6-REAL-PILOT-E2E",
    "E6-MULTITENANT-REAL",
    "E7-24H-SOAK",
    "E7-TENANT-ISOLATION-LOAD",
    "E8-VISUAL-DESKTOP",
    "E8-VISUAL-MOBILE",
    "E8-PDF-VISUAL",
    "E8-PROD-ENV-PROTECTION",
    "E8-RC-SIGNOFF",
    "F1-CONTROLLED-PILOT-AUTH",
}
missing_required = sorted(required_test_ids - set(ids))
if missing_required:
    raise SystemExit(f"Required manual acceptance tests missing: {missing_required}")

print(f"Manual acceptance matrix: PASS ({len(tests)} tests)")
print("All acceptance results remain PENDING until real evidence is recorded.")
