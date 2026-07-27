from __future__ import annotations

import json
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = BACKEND_DIR.parent
DASHBOARD_TRANSLATIONS_DIR = BACKEND_DIR / "app" / "translations" / "dashboard"
EXECUTIVE_REPORT_TEMPLATE = BACKEND_DIR / "app" / "templates" / "executive_report.html"
LANDING_HOME_PAGE = REPOSITORY_ROOT / "landingpage_neu" / "index.html"
LANDING_PRICING_PAGE = REPOSITORY_ROOT / "landingpage_neu" / "pricing.html"
LANDING_EXECUTIVE_REPORTS_PAGE = (
    REPOSITORY_ROOT / "landingpage_neu" / "executive-reports.html"
)
LANDING_WHY_PAGE = REPOSITORY_ROOT / "landingpage_neu" / "why-bcsentinel.html"
LANDING_I18N_LOADER = REPOSITORY_ROOT / "landingpage_neu" / "assets" / "js" / "i18n.js"
LANDING_PRODUCT_COPY_DIR = REPOSITORY_ROOT / "landingpage_neu" / "lang"
BC_SETUP_PRODUCT_COPY_EXTENSION = (
    REPOSITORY_ROOT
    / "bc-extension"
    / "app"
    / "src"
    / "pageextensions"
    / "DHSetupProductCopy.PageExt.al"
)
BC_ISSUES_PAGE = (
    REPOSITORY_ROOT
    / "bc-extension"
    / "app"
    / "src"
    / "pages"
    / "DHDashboardIssues.Page.al"
)
BC_ISSUES_LIST_PAGE = (
    REPOSITORY_ROOT
    / "bc-extension"
    / "app"
    / "src"
    / "pages"
    / "DHDashboardIssuesList.Page.al"
)


def _load(language: str) -> dict[str, str]:
    path = DASHBOARD_TRANSLATIONS_DIR / f"{language}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_assessment_is_the_customer_facing_offer_in_dashboard_copy() -> None:
    en = _load("en")
    de = _load("de")

    assert en["assessment_validation_active"] == "Assessment / Validation active"
    assert en["assessment_needed"] == "Assessment needed"
    assert en["buy_assessment"] == "Start Assessment"

    assert de["assessment_validation_active"] == "Assessment / Validation aktiv"
    assert de["assessment_needed"] == "Assessment benötigt"
    assert de["buy_assessment"] == "Assessment starten"


def test_premium_does_not_define_a_dashboard_commercial_offer() -> None:
    en = _load("en")
    de = _load("de")

    assert en.get("full_premium_analysis") == "Full Analysis"
    assert de.get("full_premium_analysis") == "Vollständige Analyse"

    assert "Buy Full Analysis" not in en.values()
    assert "Full Analysis kaufen" not in de.values()
    assert "Full Premium Analysis" not in en.values()
    assert "Full Premium Analysis" not in de.values()


def test_bc_issue_pages_use_assessment_as_the_customer_facing_offer() -> None:
    for path in (BC_ISSUES_PAGE, BC_ISSUES_LIST_PAGE):
        content = path.read_text(encoding="utf-8-sig")

        assert "Label 'Start Assessment for detailed insights'" in content
        assert "Label 'Buy Full Analysis for detailed insights'" not in content

        # The existing variable name remains stable because this wave changes
        # localized display copy only and does not rename technical identifiers.
        assert "BuyFullAnalysisLbl" in content


def test_bc_setup_actions_use_canonical_offer_copy_with_legacy_action_names() -> None:
    content = BC_SETUP_PRODUCT_COPY_EXTENSION.read_text(encoding="utf-8-sig")

    assert "modify(BuyFullAnalysis)" in content
    assert "Caption = 'Start Assessment';" in content
    assert "checkout for an Assessment" in content
    assert "Caption = 'Start Validation Check';" in content
    assert "Caption = 'Start Monitoring Monthly';" in content
    assert "Caption = 'Start Monitoring Annual';" in content

    # Existing action names remain stable; only display copy is overridden.
    assert "modify(BuyValidationCheck)" in content
    assert "modify(StartMonitoringMonthly)" in content
    assert "modify(StartMonitoringAnnual)" in content
    assert "Buy Full Analysis" not in content


def test_executive_report_uses_canonical_commercial_offer_copy() -> None:
    content = EXECUTIVE_REPORT_TEMPLATE.read_text(encoding="utf-8")

    assert "<h2>Assessment starten</h2>" in content
    assert ">ASSESSMENT STARTEN <" in content
    assert "<h2>Monitoring starten</h2>" in content
    assert ">MONITORING STARTEN <" in content
    assert "Verfügbar mit Assessment oder Monitoring" in content

    assert "Upgrade zur vollständigen Analyse" not in content
    assert "ZUR VOLLSTÄNDIGEN ANALYSE" not in content
    assert "BCSentinel Premium-Angeboten" not in content


def test_landing_home_uses_canonical_offer_copy_with_legacy_checkout_codes() -> None:
    content = LANDING_HOME_PAGE.read_text(encoding="utf-8")

    assert ">Assessment starten</a>" in content
    assert "<span>A</span>Assessment" in content
    assert "<h3>Assessment</h3>" in content
    assert ">Validation Check starten</a>" in content
    assert ">Monitoring starten</a>" in content

    assert ">Full Analysis starten</a>" not in content
    assert "<span>F</span>Full Analysis" not in content
    assert "<h3>Full Analysis</h3>" not in content

    # The historical integration identifier remains stable for checkout routing.
    assert 'data-product-code="full_analysis"' in content
    assert 'data-checkout-product="full_analysis"' in content
    assert "contact.html?intent=full_analysis" in content


def test_landing_pricing_uses_assessment_without_renaming_checkout_codes() -> None:
    content = LANDING_PRICING_PAGE.read_text(encoding="utf-8")

    assert "<h3>Assessment</h3>" in content
    assert ">Assessment starten</a>" in content
    assert "<th>Assessment</th>" in content
    assert ">Monitoring starten</a>" in content

    assert "<h3>Full Analysis</h3>" not in content
    assert ">Full Analysis freischalten</a>" not in content
    assert ">Full Analysis starten</a>" not in content

    # Existing integration codes are compatibility identifiers, not display copy.
    assert 'data-product-code="full_analysis"' in content
    assert 'data-checkout-product="full_analysis"' in content
    assert "contact.html?intent=full_analysis" in content


def test_landing_assessment_pages_use_one_compatible_checkout_identifier() -> None:
    for path in (LANDING_EXECUTIVE_REPORTS_PAGE, LANDING_WHY_PAGE):
        content = path.read_text(encoding="utf-8")

        assert ">Assessment starten</a>" in content
        assert 'data-product-code="full_analysis"' in content
        assert 'data-checkout-product="full_analysis"' in content
        assert "contact.html?intent=full_analysis" in content

        assert 'data-product-code="assessment"' not in content
        assert 'data-checkout-product="assessment"' not in content
        assert "contact.html?intent=assessment" not in content


def test_landing_product_copy_overlays_are_canonical_and_loaded_last() -> None:
    de = json.loads(
        (LANDING_PRODUCT_COPY_DIR / "product-copy.de.json").read_text(encoding="utf-8")
    )
    en = json.loads(
        (LANDING_PRODUCT_COPY_DIR / "product-copy.en.json").read_text(encoding="utf-8")
    )
    loader = LANDING_I18N_LOADER.read_text(encoding="utf-8")

    assert de["cta_assessment"] == "Assessment starten"
    assert en["nav_cta"] == "Start Assessment"
    assert en["product_assessment_badge"] == "Assessment"
    assert en["plan_assessment_cta"] == "Start Assessment"

    for values in (de.values(), en.values()):
        assert all("Full Premium Analysis" not in value for value in values)
        assert all("Buy Full Analysis" not in value for value in values)

    assert "lang/product-copy.${code}.json" in loader
    assert "{ ...(base[code] || {}), ...(overlays[code] || {}) }" in loader
    assert "Could not load product copy overlay language file" in loader


def test_legacy_translation_keys_remain_stable() -> None:
    en = _load("en")
    de = _load("de")

    for key in (
        "full_analysis",
        "full_premium_analysis",
        "validation_check",
        "monitoring",
        "buy_assessment",
    ):
        assert key in en
        assert key in de
