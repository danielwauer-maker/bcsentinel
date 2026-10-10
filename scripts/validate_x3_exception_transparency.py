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
migration_0028 = (ROOT / "backend" / "alembic" / "versions" / "0028_scan_exception_snapshots.py").read_text(encoding="utf-8")
migration_0029 = (ROOT / "backend" / "alembic" / "versions" / "0029_exception_snapshot_capture_header.py").read_text(encoding="utf-8")
dashboard_api = (ROOT / "dashboard" / "src" / "api" / "corePages.ts").read_text(encoding="utf-8")
dashboard_hooks = (ROOT / "dashboard" / "src" / "core" / "hooks.ts").read_text(encoding="utf-8")
dashboard_types = (ROOT / "dashboard" / "src" / "core" / "types.ts").read_text(encoding="utf-8")
app_shell = (ROOT / "dashboard" / "src" / "foundation" / "AppShell.tsx").read_text(encoding="utf-8")
report_v2 = (ROOT / "backend" / "app" / "services" / "executive_report_v2_service.py").read_text(encoding="utf-8")
transport_path = ROOT / "bc-extension" / "app" / "src" / "codeunits" / "DHExceptionSnapshotTransport.Codeunit.al"

if contract["authority"]["exception_management"] != "business_central":
    raise SystemExit("Exception management authority must remain Business Central.")
if contract["write_model"]["immutable_after_first_capture"] is not True:
    raise SystemExit("Per-scan exception snapshots must be immutable after first capture.")

for needle in ('class ScanExceptionSnapshotCapture','__tablename__ = "scan_exception_snapshot_captures"','class ScanExceptionSnapshot','__tablename__ = "scan_exception_snapshots"','UniqueConstraint(','"scan_id"','"source_exception_entry_no"','issue_code','reason','captured_at_utc'):
    if needle not in model:
        raise SystemExit(f"X3 snapshot model fragment missing: {needle}")
for needle in ('@router.post("/scans/{scan_id}/exception-snapshot")','@router.get("/scans/{scan_id}/exceptions")','Machine tenant credentials are required.','Exception snapshot is immutable once captured for a scan.','snapshot_captured','exceptions_applied','captured_exception_count','ScanExceptionSnapshotCapture('):
    if needle not in router:
        raise SystemExit(f"X3 API fragment missing: {needle}")
if 'router.include_router(exception_transparency_router)' not in license_router:
    raise SystemExit("X3 exception transparency router is not mounted in runtime.")
if 'router.include_router(prepilot_router)' not in license_router:
    raise SystemExit("Pre-pilot account/commercial routers are not mounted in runtime.")
if 'tenant_auth_router' in prepilot:
    raise SystemExit("Pre-pilot aggregator must not duplicate the already-mounted tenant auth router.")
if 'revision = "0028_scan_exception_snapshots"' not in migration_0028 or 'down_revision = "0027_operations_governance"' not in migration_0028:
    raise SystemExit("X3 base Alembic chain is not anchored to 0027_operations_governance.")
if 'revision = "0029_exception_snapshot_capture_header"' not in migration_0029 or 'down_revision = "0028_scan_exception_snapshots"' not in migration_0029:
    raise SystemExit("X3 capture-header migration is not anchored to 0028_scan_exception_snapshots.")
if 'INSERT INTO scan_exception_snapshot_captures' not in migration_0029:
    raise SystemExit("X3 capture-header migration must preserve legacy non-empty snapshot immutability.")
for needle in ('loadScanExceptions', '/scans/${encode(scanId)}/exceptions'):
    if needle not in dashboard_api:
        raise SystemExit(f"X3 dashboard API fragment missing: {needle}")
if 'useScanExceptions' not in dashboard_hooks:
    raise SystemExit("X3 dashboard hook for exception snapshots is missing.")
for needle in ('ScanExceptionSnapshot', 'snapshot_captured', 'exceptions_applied'):
    if needle not in dashboard_types:
        raise SystemExit(f"X3 dashboard type fragment missing: {needle}")
for needle in ('exception-scope-banner', 'Ausnahmen anzeigen', 'Historischer Snapshot'):
    if needle not in app_shell:
        raise SystemExit(f"X3 dashboard transparency fragment missing: {needle}")
if 'exception' not in report_v2.lower():
    raise SystemExit("X3 exception evidence is not connected to the Executive Report layer.")

if contract.get("bc_transport_status") == "complete":
    if not transport_path.exists():
        raise SystemExit("X3 claims complete BC transport but the transport codeunit is missing.")
    transport = transport_path.read_text(encoding="utf-8")
    for needle in (
        'EventSubscriber(ObjectType::Table, Database::"DH Deep Scan Run", \'OnAfterModifyEvent\'',
        'Rec.Status <> Rec.Status::Completed',
        '[TryFunction]',
        'SecretMgt.GetApiToken(Setup)',
        'IssueException.SetRange(Active, true)',
        "'/scans/' + Format(ScanId) + '/exception-snapshot'",
        "RequestHeaders.Add('X-Tenant-Id', Setup.\"Tenant ID\")",
        "RequestHeaders.Add('X-Api-Token', ApiToken)",
        'Response.HttpStatusCode() = 409',
        "Payload.Add('exceptions', Exceptions)",
    ):
        if needle not in transport:
            raise SystemExit(f"X3 BC transport fragment missing: {needle}")
    if contract.get("open_evidence"):
        raise SystemExit("X3 transport is complete but open_evidence is not empty.")

print("X3 exception transparency contract: PASS")
print(f"X3 BC snapshot transport: {'READY' if transport_path.exists() else 'OPEN'}")
