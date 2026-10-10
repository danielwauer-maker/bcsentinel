#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "config" / "x3-exception-transparency.json").read_text(encoding="utf-8"))
model = (ROOT / "backend" / "app" / "exception_snapshot_models.py").read_text(encoding="utf-8")
router = (ROOT / "backend" / "app" / "routers" / "exception_transparency.py").read_text(encoding="utf-8")
license_router = (ROOT / "backend" / "app" / "routers" / "license.py").read_text(encoding="utf-8")
prepilot = (ROOT / "backend" / "app" / "routers" / "prepilot.py").read_text(encoding="utf-8")
migration = (ROOT / "backend" / "alembic" / "versions" / "0028_scan_exception_snapshots.py").read_text(encoding="utf-8")

if contract["authority"]["exception_management"] != "business_central":
    raise SystemExit("Exception management authority must remain Business Central.")
if contract["write_model"]["immutable_after_first_capture"] is not True:
    raise SystemExit("Per-scan exception snapshots must be immutable after first capture.")

for needle in (
    'class ScanExceptionSnapshot',
    '__tablename__ = "scan_exception_snapshots"',
    'UniqueConstraint(',
    '"scan_id"',
    '"source_exception_entry_no"',
    'issue_code',
    'reason',
    'captured_at_utc',
):
    if needle not in model:
        raise SystemExit(f"X3 snapshot model fragment missing: {needle}")

for needle in (
    '@router.post("/scans/{scan_id}/exception-snapshot")',
    '@router.get("/scans/{scan_id}/exceptions")',
    'Machine tenant credentials are required.',
    'Exception snapshot is immutable once captured for a scan.',
    'exceptions_applied',
    'captured_exception_count',
):
    if needle not in router:
        raise SystemExit(f"X3 API fragment missing: {needle}")

if 'router.include_router(exception_transparency_router)' not in license_router:
    raise SystemExit("X3 exception transparency router is not mounted in runtime.")
if 'router.include_router(prepilot_router)' not in license_router:
    raise SystemExit("Pre-pilot account/commercial routers are not mounted in runtime.")
if 'tenant_auth_router' in prepilot:
    raise SystemExit("Pre-pilot aggregator must not duplicate the already-mounted tenant auth router.")
if 'revision = "0028_scan_exception_snapshots"' not in migration or 'down_revision = "0027_operations_governance"' not in migration:
    raise SystemExit("X3 Alembic chain is not anchored to 0027_operations_governance.")

print("X3 exception transparency contract: PASS")
