from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PUBLIC_FILES = sorted((ROOT / "landingpage_neu").glob("*.html")) + [
    ROOT / "landingpage_neu" / "lang" / "de.json",
    ROOT / "landingpage_neu" / "lang" / "en.json",
]

FORBIDDEN_CLAIMS = [
    "Available on Microsoft AppSource",
    "Hosted in Microsoft Azure",
    "GDPR compliant",
    "Enterprise ready",
    "Business-Central-Aktionen",
    "Benjamin Schroyer",
    "100+",
    "+49 89 123 456 789",
    "Maximilianstrasse 35",
    "BCSentinel GmbH",
    "Mo - Fr: 08:00 - 18:00 Uhr",
    "99.99 %",
    "99.98 %",
    "frontendseitig vorbereitet",
    "submit endpoint will be connected separately",
]


def test_public_landing_does_not_publish_unverified_claims() -> None:
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in PUBLIC_FILES)
    for claim in FORBIDDEN_CLAIMS:
        assert claim not in corpus, f"Unverified public claim found: {claim}"


def test_current_monitoring_offer_does_not_claim_future_controlled_actions() -> None:
    pricing = (ROOT / "landingpage_neu" / "pricing.html").read_text(encoding="utf-8")
    assert 'data-i18n="price_feature_actions"' not in pricing


def test_pilot_page_is_explicitly_capped_and_non_production() -> None:
    pilot = (ROOT / "landingpage_neu" / "pilot.html").read_text(encoding="utf-8")
    assert "bis zu 50" in pilot.lower()
    assert "keine allgemeine produktionsfreigabe" in pilot.lower()
    assert "AppSource" in pilot


def test_contact_surface_uses_real_api_submit_and_safe_fallback_copy() -> None:
    contact = (ROOT / "landingpage_neu" / "contact.html").read_text(encoding="utf-8")
    assert "data-contact-form" in contact
    assert '"/public/contact"' in contact
    assert "privacy_accepted" in contact
    assert "support@bcsentinel.com" in contact


def test_current_legal_surfaces_are_present_and_explicitly_marked_for_manual_review() -> None:
    for name in ("impressum.html", "privacy.html", "terms.html", "dpa.html"):
        content = (ROOT / "landingpage_neu" / name).read_text(encoding="utf-8")
        assert "keine Rechtsberatung" in content
        assert "pruef" in content.lower()


def test_docs_media_placeholders_explain_what_must_be_captured() -> None:
    docs = (ROOT / "landingpage_neu" / "docs.html").read_text(encoding="utf-8")
    for expected in (
        "Screenshot: BC Setup",
        "Screenshot: Scan History",
        "Screenshot: Dashboard Overview",
        "Screenshot: Finding Detail",
        "Screenshot: Executive Report",
        "Screenshot: Monitoring",
        "Quick Start",
        "Scan Walkthrough",
        "Executive Report",
    ):
        assert expected in docs
