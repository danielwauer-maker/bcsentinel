#!/usr/bin/env python3
"""Static legal-readiness audit for BCSentinel landing-page content."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "landingpage" / "lang"
RUNTIME = ROOT / "landingpage" / "js" / "content-runtime.js"

LEGAL_BUNDLES = ("impressum", "privacy", "terms", "contact")

# Detect only genuine publishing placeholders or declarations that the visible
# legal text is still a draft. Operational disclosures such as a planned
# FormSubmit-to-Brevo migration must remain allowed and transparent.
FORBIDDEN = (
    # Literal editorial placeholders only. The opening marker must start with
    # one of the known placeholder phrases; ordinary JSON arrays are excluded.
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
    terms_de = serialized("terms", "de")
    contact_de = serialized("contact", "de")
    runtime = RUNTIME.read_text(encoding="utf-8")

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
        "terms.de.json: entrepreneur-only scope": (terms_de, "§ 14 BGB"),
        "terms.de.json: contract formation": (terms_de, "Stripe-Checkouts"),
        "terms.de.json: liability": (terms_de, "Vorsatz und grober Fahrlässigkeit"),
        "terms.de.json: German law": (terms_de, "deutsches Recht"),
        "contact.de.json: privacy acknowledgement": (contact_de, "zur Kenntnis genommen"),
        "content-runtime.js: small-business price normalization": (runtime, "Kleinunternehmerregelung gemäß § 19 UStG"),
        "content-runtime.js: Google Fonts disclosure": (runtime, "Google Fonts"),
    }
    for label, (text, marker) in required.items():
        if marker not in text:
            errors.append(f"{label} missing")

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
    print("- separate Article 28 DPA and first-party Brevo contact sprint remain operational deliverables")
    return 0


if __name__ == "__main__":
    sys.exit(main())
