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


def test_contact_surface_has_real_email_handoff_not_fake_submit() -> None:
    contact = (ROOT / "landingpage_neu" / "contact.html").read_text(encoding="utf-8")
    assert "mailto:support@bcsentinel.com" in contact
    assert "data-contact-form" not in contact
