#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
audit = json.loads((ROOT / "config" / "x8-pre-manual-pilot-audit.json").read_text(encoding="utf-8"))

if audit.get("official_go_live_readiness_owned_here") is not False:
    raise SystemExit("X8 must not own or recompute official go-live readiness.")

for relative in audit["required_contracts"]:
    if not (ROOT / relative).exists():
        raise SystemExit(f"Missing X8 prerequisite contract: {relative}")

x3 = json.loads((ROOT / "config" / "x3-exception-transparency.json").read_text(encoding="utf-8"))
x6 = json.loads((ROOT / "config" / "x6-legal-review.json").read_text(encoding="utf-8"))
x7 = json.loads((ROOT / "config" / "x7-dev-acceptance.json").read_text(encoding="utf-8"))
workflow = (ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
dashboard_root = ROOT / "dashboard" / "src"
landing_root = ROOT / "landingpage"

# Deployment safety: main must never implicitly deploy PROD.
if "branches:\n      - main" in workflow or "github.ref == 'refs/heads/main'" in workflow:
    raise SystemExit("X8 P0: automatic main→PROD deployment is present.")
if "workflow_dispatch:" not in workflow or "PROMOTE_TO_PROD" not in workflow:
    raise SystemExit("X8 P0: controlled manual PROD promotion evidence is missing.")
if "dev.bcsentinel.com" not in workflow or "dev-api.bcsentinel.com" not in workflow:
    raise SystemExit("X8 P0: DEV acceptance hosts are not explicit in deployment workflow.")

# Dashboard remains read-only with respect to BC operational authority.
dashboard_text = "\n".join(path.read_text(encoding="utf-8") for path in dashboard_root.rglob("*.ts*") if path.is_file())
for forbidden in (
    "/scan/start",
    "/scan/reconcile",
    "/exception-snapshot",
    "remediation/actions/complete",
    "remediation/actions/create",
    "scheduler/update",
):
    if forbidden in dashboard_text:
        raise SystemExit(f"X8 P0: forbidden dashboard write surface detected: {forbidden}")

# Legal surface may be a review candidate, but must never pretend approval.
if x6.get("legal_approval_claimed") is not False or x6.get("status") != "review_candidate":
    raise SystemExit("X8 P0: legal review boundary is not explicit.")
legal_text = "\n".join((landing_root / name).read_text(encoding="utf-8").lower() for name in ("impressum.html", "privacy.html", "terms.html"))
for forbidden in (
    "§ 5 tmg",
    "ec.europa.eu/consumers/odr",
    "[telefonnummer]",
    "[ust-idnr.]",
    "[registernummer]",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
):
    if forbidden in legal_text:
        raise SystemExit(f"X8 P0: stale/placeholder legal fragment detected: {forbidden}")

# Public/product canonical financial language must not regress to public ROI.
report_schema = (ROOT / "backend" / "app" / "schemas" / "report.py").read_text(encoding="utf-8")
if "roi_eur" in report_schema:
    raise SystemExit("X8 P0: legacy ROI is present in the public report schema.")

# Old prototype pricing literals must not return to production landing surfaces.
landing_text = "\n".join(path.read_text(encoding="utf-8") for path in landing_root.rglob("*.html") if path.is_file())
for legacy in ("79 €/", "49 €/", "149 €/", "79€", "49€", "149€"):
    if legacy in landing_text:
        raise SystemExit(f"X8 P0: legacy pricing literal detected: {legacy}")

# Audit must truthfully reflect X3 until the trusted BC transport is present.
blocker_ids = {item["id"] for item in audit.get("code_blockers", [])}
if x3.get("bc_transport_status") != "complete":
    if "X3-BC-EXCEPTION-TRANSPORT" not in blocker_ids:
        raise SystemExit("X8 P0: X3 BC transport is open but absent from the blocker list.")
    if audit.get("status") == "ready":
        raise SystemExit("X8 cannot be ready while X3 BC transport remains open.")

if x7.get("acceptance_environment") != "dev.bcsentinel.com":
    raise SystemExit("X8 P0: authoritative DEV acceptance environment drifted.")

print("X8 Pre-Manual Pilot Audit contract: PASS")
print(f"X8 status: {audit.get('status')}")
print(f"Code blockers: {len(audit.get('code_blockers', []))}")
print(f"External evidence items: {len(audit.get('external_evidence', []))}")
print(f"Manual acceptance items: {len(audit.get('manual_acceptance', []))}")
