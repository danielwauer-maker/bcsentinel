#!/usr/bin/env python3
"""Static legal-readiness audit for BCSentinel landing-page content."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "landingpage"
LANG = LANDING / "lang"
RUNTIME = LANDING / "js" / "content-runtime.js"
PRICING = LANDING / "js" / "pricing-conversion-journey.js"
LEGAL_DOCS = ROOT / "docs" / "legal"
EXCLUDED_HTML = {"blueprint.html", "design-system.html"}

LEGAL_BUNDLES = ("impressum", "privacy", "terms", "contact")

# Detect only genuine publishing placeholders or declarations that the visible
# legal text is still a draft. Operational disclosures such as a planned
# FormSubmit-to-Brevo migration must remain allowed and transparent.
FORBIDDEN = (
    re.compile(r"\[(?:noch\b|to be\b|add\b|falls\b|if\b)[^\[\]\r\n]{0,180}\]", re.I),
    re.compile(r"\bArbeitsfassung\b|\bworking draft\b", re.I),
    re.compile(r"\b(?:rechtlich|abschließend) zu finalisieren\b", re.I),
    re.compile(r"\bmust be legally finali[sz]ed\b", re.I),
    re.compile(r"\b(?:vor|before) (?:dem |the )?(?:öffentlichen |public )?Go-Live zu ergänzen\b", re.I),
    re.compile(r"\bto be (?:added|completed) before (?:public )?go-live\b", re.I),
)


def load(bundle: str, locale: str) -> dict:
    path = LANG / f"{bundle}.{locale}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def serialized(bundle: str, locale: str) -> str:
    return json.dumps(load(bundle, locale), ensure_ascii=False)


def audit_external_fonts() -> list[str]:
    errors: list[str] = []
    for path in sorted(LANDING.glob("*.html")):
        if path.name in EXCLUDED_HTML:
            continue
        text = path.read_text(encoding="utf-8")
        if "fonts.googleapis.com" in text or "fonts.gstatic.com" in text:
            errors.append(f"{path.name}: external Google Fonts reference remains")
    return errors


def audit_operational_documents() -> list[str]:
    errors: list[str] = []
    required = {
        "SUBPROCESSORS.md": (
            ("Hetzner Online GmbH",),
            ("Stripe Payments Europe",),
            ("FormSubmit",),
            ("Brevo",),
        ),
        "RETENTION_AND_DELETION_CONCEPT.md": (
            ("Server-Zugriffslogs", "Webserver-Zugriffslogs"),
            ("14 Tage",),
            ("90 Tage",),
            ("Backups",),
            ("Löschablauf bei Vertragsende",),
        ),
        "CHECKOUT_LEGAL_REQUIREMENTS.md": (
            ("§ 14 BGB",),
            ("§ 19 UStG",),
            ("Stripe-Checkout-Session",),
            ("B2B-Bestätigung",),
            ("Nutzungsbedingungen",),
        ),
    }
    for filename, marker_groups in required.items():
        path = LEGAL_DOCS / filename
        if not path.exists():
            errors.append(f"docs/legal/{filename}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        for alternatives in marker_groups:
            if not any(marker in text for marker in alternatives):
                expected = " or ".join(alternatives)
                errors.append(f"docs/legal/{filename}: required marker missing ({expected})")
    return errors


def main() -> int:
    errors: list[str] = []
    for bundle in LEGAL_BUNDLES:
        de = load(bundle, "de")
        en = load(bundle, "en")
        if de.get("meta", {}).get("schema_version") != "lp-legal-01-v1":
            errors.append(f"{bundle}.de.json: legal schema version missing")
        if en.get("meta", {}).get("schema_version") != "lp-legal-01-v1":
            errors.append(f"{bundle}.en.json: legal schema version missing")
        for locale, payload in (("de", de), ("en", en)):
            text = json.dumps(payload, ensure_ascii=False)
            for pattern in FORBIDDEN:
                match = pattern.search(text)
                if match:
                    errors.append(
                        f"{bundle}.{locale}.json: draft or placeholder language detected "
                        f"({match.group(0)!r})"
                    )

    impressum_de = serialized("impressum", "de")
    privacy_de = serialized("privacy", "de")
    privacy_en = serialized("privacy", "en")
    terms_de = serialized("terms", "de")
    contact_de = serialized("contact", "de")
    runtime = RUNTIME.read_text(encoding="utf-8")
    pricing = PRICING.read_text(encoding="utf-8")

    required = {
        "impressum.de.json: provider identity": (impressum_de, "Daniel Wauer"),
        "impressum.de.json: business name": (impressum_de, "BCSentinel"),
        "impressum.de.json: B2B restriction": (impressum_de, "§ 14 BGB"),
        "impressum.de.json: small-business VAT": (impressum_de, "§ 19 UStG"),
        "privacy.de.json: Hetzner Falkenstein": (privacy_de, "Falkenstein"),
        "privacy.de.json: Stripe": (privacy_de, "Stripe"),
        "privacy.de.json: temporary FormSubmit disclosure": (privacy_de, "FormSubmit"),
        "privacy.de.json: planned Brevo delivery": (privacy_de, "Brevo"),
        "privacy.de.json: Article 28 processing": (privacy_de, "Art. 28 DSGVO"),
        "privacy.de.json: supervisory authority": (privacy_de, "Hintere Bleiche 34"),
        "privacy.de.json: system fonts": (privacy_de, "keine Schriftanfrage an Google Fonts"),
        "privacy.en.json: system fonts": (privacy_en, "does not send a font request to Google Fonts"),
        "terms.de.json: entrepreneur-only scope": (terms_de, "§ 14 BGB"),
        "terms.de.json: contract formation": (terms_de, "Stripe-Checkouts"),
        "terms.de.json: liability": (terms_de, "Vorsatz und grober Fahrlässigkeit"),
        "terms.de.json: German law": (terms_de, "deutsches Recht"),
        "contact.de.json: privacy acknowledgement": (contact_de, "zur Kenntnis genommen"),
        "content-runtime.js: small-business price normalization": (runtime, "Kleinunternehmerregelung gemäß § 19 UStG"),
        "content-runtime.js: system-font normalization": (runtime, "keine Schriftanfrage an Google Fonts"),
        "pricing-conversion-journey.js: B2B buyer notice": (pricing, "Ausschließlich für Geschäftskunden"),
        "pricing-conversion-journey.js: entrepreneur confirmation": (pricing, "§ 14 BGB"),
        "pricing-conversion-journey.js: small-business notice": (pricing, "§ 19 UStG"),
    }
    for label, (text, marker) in required.items():
        if marker not in text:
            errors.append(f"{label} missing")

    errors.extend(audit_external_fonts())
    errors.extend(audit_operational_documents())

    if errors:
        print("Landing legal audit FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Landing legal audit PASS")
    print("- provider is Daniel Wauer using BCSentinel as business and product name")
    print("- offer is restricted to entrepreneurs under section 14 BGB")
    print("- small-business VAT treatment under section 19 UStG is represented")
    print("- Hetzner, Stripe, temporary FormSubmit and planned Brevo use are disclosed")
    print("- privacy, B2B terms and contact acknowledgement contain no legal placeholders")
    print("- no public page loads Google Fonts or another Google font endpoint")
    print("- pricing journey contains visible B2B and small-business notices")
    print("- subprocessor register, retention concept and checkout requirements are documented")
    print("- separate Article 28 DPA and first-party Brevo contact sprint remain operational deliverables")
    return 0


if __name__ == "__main__":
    sys.exit(main())
