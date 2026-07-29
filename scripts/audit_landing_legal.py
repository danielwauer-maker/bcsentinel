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
CONTACT_JS = LANDING / "js" / "contact-page.js"
PUBLIC_ROUTER = ROOT / "backend" / "app" / "routers" / "public.py"
CONTACT_SERVICE = ROOT / "backend" / "app" / "services" / "public_contact_service.py"
CONTACT_TESTS = ROOT / "backend" / "tests" / "test_public_contact.py"
CONTACT_OPS = ROOT / "docs" / "ops" / "public-contact-delivery.md"
LEGAL_DOCS = ROOT / "docs" / "legal"
EXCLUDED_HTML = {"blueprint.html", "design-system.html"}

LEGAL_BUNDLES = ("impressum", "privacy", "terms", "contact")

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
            ("Brevo",),
            ("aktiv für Kontaktzustellung",),
            ("FormSubmit ist seit LP-LEGAL-02 nicht mehr Bestandteil",),
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


def audit_contact_delivery() -> list[str]:
    errors: list[str] = []
    required_files = (CONTACT_JS, PUBLIC_ROUTER, CONTACT_SERVICE, CONTACT_TESTS, CONTACT_OPS)
    for path in required_files:
        if not path.exists():
            errors.append(f"{path.relative_to(ROOT)}: missing")
    if errors:
        return errors

    frontend = CONTACT_JS.read_text(encoding="utf-8")
    router = PUBLIC_ROUTER.read_text(encoding="utf-8")
    service = CONTACT_SERVICE.read_text(encoding="utf-8")
    tests = CONTACT_TESTS.read_text(encoding="utf-8")
    ops = CONTACT_OPS.read_text(encoding="utf-8")

    if "formsubmit.co" in frontend.lower() or "FORM_ENDPOINT" in frontend:
        errors.append("landingpage/js/contact-page.js: FormSubmit integration remains")

    markers = {
        "landingpage/js/contact-page.js: first-party endpoint": (frontend, "/public/contact"),
        "landingpage/js/contact-page.js: JSON delivery": (frontend, "JSON.stringify(payload)"),
        "landingpage/js/contact-page.js: production API domain": (frontend, "https://api.bcsentinel.com"),
        "backend public router: endpoint": (router, '@router.post("/public/contact"'),
        "backend public router: rate limiting": (router, "require_rate_limit"),
        "backend public router: honeypot": (router, "payload.website"),
        "backend public router: content filter": (router, "message contains too many external links"),
        "backend contact service: Brevo-compatible SMTP": (service, "smtplib.SMTP"),
        "backend contact service: recipient setting": (service, "CONTACT_RECIPIENT_EMAIL"),
        "backend contact service: reply-to": (service, 'message["Reply-To"]'),
        "backend contact tests: success": (tests, "test_public_contact_delivers_message"),
        "backend contact tests: honeypot": (tests, "test_public_contact_honeypot_is_accepted_without_delivery"),
        "backend contact tests: rate limit": (tests, "test_public_contact_rate_limit"),
        "contact operations: Brevo host": (ops, "smtp-relay.brevo.com"),
        "contact operations: secret handling": (ops, "Secret Store"),
    }
    for label, (text, marker) in markers.items():
        if marker not in text:
            errors.append(f"{label} missing")
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
    contact_en = serialized("contact", "en")
    runtime = RUNTIME.read_text(encoding="utf-8")
    pricing = PRICING.read_text(encoding="utf-8")

    required = {
        "impressum.de.json: provider identity": (impressum_de, "Daniel Wauer"),
        "impressum.de.json: business name": (impressum_de, "BCSentinel"),
        "impressum.de.json: B2B restriction": (impressum_de, "§ 14 BGB"),
        "impressum.de.json: small-business VAT": (impressum_de, "§ 19 UStG"),
        "privacy.de.json: Hetzner Falkenstein": (privacy_de, "Falkenstein"),
        "privacy.de.json: Stripe": (privacy_de, "Stripe"),
        "privacy.de.json: first-party endpoint": (privacy_de, "eigenen BCSentinel-Backend-Endpunkt"),
        "privacy.de.json: active Brevo delivery": (privacy_de, "Brevo an support@bcsentinel.com"),
        "privacy.de.json: Article 28 processing": (privacy_de, "Art. 28 DSGVO"),
        "privacy.de.json: supervisory authority": (privacy_de, "Hintere Bleiche 34"),
        "privacy.de.json: system fonts": (privacy_de, "keine Schriftanfrage an Google Fonts"),
        "privacy.en.json: first-party endpoint": (privacy_en, "first-party BCSentinel backend endpoint"),
        "privacy.en.json: active Brevo delivery": (privacy_en, "through Brevo"),
        "privacy.en.json: system fonts": (privacy_en, "does not send a font request to Google Fonts"),
        "terms.de.json: entrepreneur-only scope": (terms_de, "§ 14 BGB"),
        "terms.de.json: contract formation": (terms_de, "Stripe-Checkouts"),
        "terms.de.json: liability": (terms_de, "Vorsatz und grober Fahrlässigkeit"),
        "terms.de.json: German law": (terms_de, "deutsches Recht"),
        "contact.de.json: privacy acknowledgement": (contact_de, "zur Kenntnis genommen"),
        "contact.de.json: first-party contact security": (contact_de, "eigenen BCSentinel-Backend-Endpunkt und Brevo"),
        "contact.en.json: first-party contact security": (contact_en, "first-party BCSentinel backend endpoint and Brevo"),
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
    errors.extend(audit_contact_delivery())

    if errors:
        print("Landing legal audit FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Landing legal audit PASS")
    print("- provider is Daniel Wauer using BCSentinel as business and product name")
    print("- offer is restricted to entrepreneurs under section 14 BGB")
    print("- small-business VAT treatment under section 19 UStG is represented")
    print("- Hetzner, Stripe and active Brevo contact delivery are disclosed")
    print("- FormSubmit is removed from the public contact implementation")
    print("- first-party contact endpoint includes validation, honeypot, content limits and rate limiting")
    print("- public contact delivery has automated endpoint tests and operating documentation")
    print("- privacy, B2B terms and contact acknowledgement contain no legal placeholders")
    print("- no public page loads Google Fonts or another Google font endpoint")
    print("- pricing journey contains visible B2B and small-business notices")
    print("- subprocessor register, retention concept and checkout requirements are documented")
    print("- separate Article 28 DPA and production Brevo credential verification remain operational deliverables")
    return 0


if __name__ == "__main__":
    sys.exit(main())
