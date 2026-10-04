from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PUBLIC_FILES = [
    ROOT / "landingpage_neu" / "index.html",
    ROOT / "landingpage_neu" / "pricing.html",
    ROOT / "landingpage_neu" / "trust.html",
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
]


def test_public_landing_does_not_publish_unverified_claims() -> None:
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in PUBLIC_FILES)
    for claim in FORBIDDEN_CLAIMS:
        assert claim not in corpus, f"Unverified public claim found: {claim}"


def test_current_monitoring_offer_does_not_claim_future_controlled_actions() -> None:
    pricing = (ROOT / "landingpage_neu" / "pricing.html").read_text(encoding="utf-8")
    assert 'data-i18n="price_feature_actions"' not in pricing
