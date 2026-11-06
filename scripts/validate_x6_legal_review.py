#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "config" / "x6-legal-review.json").read_text(encoding="utf-8"))

if contract.get("status") != "review_candidate" or contract.get("legal_approval_claimed") is not False:
    raise SystemExit("X6 must remain an explicitly non-approved legal review candidate.")

public_paths = [ROOT / value for value in contract["public_surfaces"]]
for path in public_paths:
    if not path.exists():
        raise SystemExit(f"Missing X6 public legal surface: {path}")
    content = path.read_text(encoding="utf-8")
    lowered = content.lower()
    for forbidden in (
        "§ 5 tmg",
        "ec.europa.eu/consumers/odr",
        "fonts.googleapis.com",
        "fonts.gstatic.com",
        "[telefonnummer]",
        "[ust-idnr.]",
        "[registernummer]",
        "[zuständiges registergericht]",
    ):
        if forbidden in lowered:
            raise SystemExit(f"Forbidden legacy/placeholder legal fragment {forbidden!r} in {path.name}")

impressum = (ROOT / "landingpage" / "impressum.html").read_text(encoding="utf-8")
if "§ 5 DDG" not in impressum:
    raise SystemExit("Legal notice must use the current § 5 DDG provider-information basis.")
if "Review Candidate" not in impressum:
    raise SystemExit("Legal notice must expose review-candidate status before legal sign-off.")

privacy = (ROOT / "landingpage" / "privacy.html").read_text(encoding="utf-8")
for required in (
    "Benutzerkonten, Tenants und Berechtigungen",
    "Business-Central-Daten und Analyse",
    "Abrechnung und individuelle Konditionen",
    "Support, Sicherheit, Audit und Telemetrie",
    "Unterauftragsverarbeiter und Drittlandtransfers",
):
    if required not in privacy:
        raise SystemExit(f"Privacy review candidate missing product-processing section: {required}")

terms = (ROOT / "landingpage" / "terms.html").read_text(encoding="utf-8")
for required in (
    "Controlled Pilot und Sonderkonditionen",
    "Estimated Loss, Potential Saving, Validated Improvement und Realized Saving",
    "nicht ohne ausdrückliche Vereinbarung automatisch",
    "Review Candidate",
):
    if required not in terms:
        raise SystemExit(f"Terms review candidate missing product-truth fragment: {required}")

for relative in contract["supporting_documents"]:
    path = ROOT / relative
    if not path.exists():
        raise SystemExit(f"Missing X6 supporting legal review document: {relative}")
    if "Review Candidate" not in path.read_text(encoding="utf-8"):
        raise SystemExit(f"Supporting legal document must remain review candidate: {relative}")

print("X6 Legal Review Candidate contract: PASS")
