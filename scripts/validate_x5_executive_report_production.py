#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "config" / "x5-executive-report-production.json").read_text(encoding="utf-8"))
schema = (ROOT / "backend" / "app" / "schemas" / "report.py").read_text(encoding="utf-8")
router = (ROOT / "backend" / "app" / "routers" / "reports.py").read_text(encoding="utf-8")
html = (ROOT / "backend" / "app" / "templates" / "executive_report.html").read_text(encoding="utf-8")
pdf = (ROOT / "backend" / "app" / "services" / "executive_report_pdf_service.py").read_text(encoding="utf-8")
v2 = (ROOT / "backend" / "app" / "services" / "executive_report_v2_service.py").read_text(encoding="utf-8")

if contract["financial_methodology"] != "fin-v1":
    raise SystemExit("X5 must preserve fin-v1 methodology.")
for field in ("exceptions_applied", "exception_count", "applied_exceptions", "ReportAppliedException"):
    if field not in schema:
        raise SystemExit(f"X5 report schema missing {field}")
for forbidden in ("roi_eur:", "estimated_premium_price_monthly:"):
    if forbidden in schema:
        raise SystemExit(f"Legacy public report field reintroduced: {forbidden}")
for needle in (
    "ScanExceptionSnapshot",
    "build_base_executive_report",
    '"exceptions_applied": bool(applied)',
    '"applied_exceptions": applied',
):
    if needle not in v2:
        raise SystemExit(f"X5 enriched builder fragment missing: {needle}")
for needle in (
    "from app.services.executive_report_v2_service import build_executive_report",
    "from app.services.executive_report_pdf_service import render_executive_report_pdf",
    '@router.get("/executive/{scan_id}", response_model=ExecutiveReport)',
    '@router.get("/monitoring/{scan_id}", response_model=ExecutiveReport)',
):
    if needle not in router:
        raise SystemExit(f"X5 report runtime fragment missing: {needle}")
for token in ("#14213D", "#246BFD", "#FF921F", "Applied Exceptions / Scan Scope Exclusions"):
    if token not in html:
        raise SystemExit(f"X5 HTML branding/transparency missing: {token}")
for needle in ("NAVY =", "ORANGE =", "Applied Exceptions", "%PDF-1.4"):
    if needle not in pdf:
        raise SystemExit(f"X5 PDF renderer fragment missing: {needle}")
print("X5 Executive Report Production contract: PASS")
