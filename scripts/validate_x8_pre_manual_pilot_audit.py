#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
audit = json.loads((ROOT / "config" / "x8-pre-manual-pilot-audit.json").read_text(encoding="utf-8"))

if audit.get("official_go_live_readiness_owned_here") is not False:
    raise SystemExit("X8 must not own or recompute official go-live readiness.")
if audit.get("official_sprint_done") is not False:
    raise SystemExit("X8 pre-manual audit must not claim official E8 completion.")
if audit.get("status") != "ready" or audit.get("pre_manual_ready") is not True:
    raise SystemExit("X8 must explicitly state pre-manual readiness after code blockers are closed.")
if audit.get("code_blockers"):
    raise SystemExit("X8 pre-manual readiness cannot contain code blockers.")

for relative in audit["required_contracts"]:
    if not (ROOT / relative).exists():
        raise SystemExit(f"Missing X8 prerequisite contract: {relative}")

x3 = json.loads((ROOT / "config" / "x3-exception-transparency.json").read_text(encoding="utf-8"))
x4 = json.loads((ROOT / "config" / "x4-notification-email-i18n.json").read_text(encoding="utf-8"))
x6 = json.loads((ROOT / "config" / "x6-legal-review.json").read_text(encoding="utf-8"))
x7 = json.loads((ROOT / "config" / "x7-dev-acceptance.json").read_text(encoding="utf-8"))
e4 = json.loads((ROOT / "config" / "e4-provider-contract.json").read_text(encoding="utf-8"))
e5 = json.loads((ROOT / "config" / "e5-recovery-automation.json").read_text(encoding="utf-8"))
e6 = json.loads((ROOT / "config" / "e6-synthetic-pilot-journey.json").read_text(encoding="utf-8"))
e7 = json.loads((ROOT / "config" / "e7-scale-soak.json").read_text(encoding="utf-8"))
workflow = (ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
dashboard_root = ROOT / "dashboard" / "src"
landing_root = ROOT / "landingpage"

if x3.get("status") != "complete" or x3.get("bc_transport_status") != "complete" or x3.get("open_evidence"):
    raise SystemExit("X8 P0: X3 exception transparency/BC transport is not completely closed.")
if x4.get("status") != "complete":
    raise SystemExit("X8 P0: X4 notification/email i18n code contract is not complete.")
if x4.get("official_e4_done") is not False:
    raise SystemExit("X8: X4 code closure must not impersonate E4 external acceptance.")

for contract_name, contract in (("E4", e4), ("E5", e5), ("E6", e6), ("E7", e7)):
    if contract.get("official_sprint_done") is not False:
        raise SystemExit(f"X8: {contract_name} automation must not claim official acceptance.")

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

# Legal surface remains a review candidate and must not pretend approval.
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

report_schema = (ROOT / "backend" / "app" / "schemas" / "report.py").read_text(encoding="utf-8")
if "roi_eur" in report_schema:
    raise SystemExit("X8 P0: legacy ROI is present in the public report schema.")

landing_text = "\n".join(path.read_text(encoding="utf-8") for path in landing_root.rglob("*.html") if path.is_file())
for legacy in ("79 €/", "49 €/", "149 €/", "79€", "49€", "149€"):
    if legacy in landing_text:
        raise SystemExit(f"X8 P0: legacy pricing literal detected: {legacy}")

if x7.get("environments", {}).get("dev", {}).get("web_host") != "dev.bcsentinel.com":
    raise SystemExit("X8 P0: authoritative DEV acceptance environment drifted.")
if x7.get("environments", {}).get("dev", {}).get("api_host") != "dev-api.bcsentinel.com":
    raise SystemExit("X8 P0: authoritative DEV API environment drifted.")

manual = audit.get("manual_acceptance", [])
for required in ("E3", "E4", "E5", "E6", "E7", "X1"):
    if not any(item.startswith(required) for item in manual):
        raise SystemExit(f"X8 must retain {required} manual/external acceptance evidence.")

print("X8 Pre-Manual Pilot Audit contract: PASS")
print("Known P0 code blockers: 0")
print(f"External evidence items: {len(audit.get('external_evidence', []))}")
print(f"Manual acceptance items: {len(manual)}")
print("Official Go-Live readiness remains owned outside X8.")
