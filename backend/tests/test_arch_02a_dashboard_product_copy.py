from __future__ import annotations

import json
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = BACKEND_DIR.parent
DASHBOARD_TRANSLATIONS_DIR = BACKEND_DIR / "app" / "translations" / "dashboard"
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
