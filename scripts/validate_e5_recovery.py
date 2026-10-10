#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "config" / "e5-recovery-automation.json").read_text(encoding="utf-8"))
backup = (ROOT / "scripts" / "backup_postgres.sh").read_text(encoding="utf-8")
restore = (ROOT / "scripts" / "restore_postgres.sh").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "recovery-quality.yml").read_text(encoding="utf-8")

if contract.get("official_sprint_done") is not False:
    raise SystemExit("E5 automation must not claim official sprint completion before real restore evidence.")

for needle in ("pg_dump", "--format=custom", "sha256sum", "alembic_version", "manifest.json"):
    if needle not in backup:
        raise SystemExit(f"E5 backup automation missing: {needle}")
for needle in ("sha256sum --check", "pg_restore", "--clean", "alembic_version"):
    if needle not in restore:
        raise SystemExit(f"E5 restore automation missing: {needle}")

for forbidden in (".env.prod", "STRIPE_SECRET_KEY", "SMTP_PASSWORD", "SECRET_KEY="):
    if forbidden in backup or forbidden in restore:
        raise SystemExit(f"E5 scripts must not embed operational secrets/config: {forbidden}")

for needle in (
    "postgres:16",
    "alembic upgrade head",
    "recovery_probe",
    "backup_postgres.sh",
    "restore_postgres.sh",
    "sha256",
    "upload-artifact",
):
    if needle not in workflow:
        raise SystemExit(f"E5 recovery CI missing: {needle}")

manual = set(contract.get("manual_evidence_required", []))
if not any("off-host" in item for item in manual) or not any("RTO/RPO" in item for item in manual):
    raise SystemExit("E5 contract must retain real off-host and RTO/RPO manual evidence requirements.")

print("E5 Recovery Automation contract: PASS")
print("Official E5 remains open pending real off-host restore evidence.")
