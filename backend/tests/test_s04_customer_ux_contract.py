from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "backend/app/templates/analytics_embed.html"
SCRIPT = ROOT / "backend/app/static/js/analytics-dashboard.js"
STYLE = ROOT / "backend/app/static/css/dashboard.css"
DE = ROOT / "backend/app/translations/dashboard/de.json"
EN = ROOT / "backend/app/translations/dashboard/en.json"
REPORT = ROOT / "backend/app/templates/executive_report.html"

MOJIBAKE_MARKERS = ("Ã", "Â", "â€", "â€“", "â€”")


def test_dashboard_customer_surfaces_are_utf8_clean() -> None:
    for path in (TEMPLATE, SCRIPT, DE, EN, REPORT):
        content = path.read_text(encoding="utf-8")
        for marker in MOJIBAKE_MARKERS:
            assert marker not in content, f"{path} contains mojibake marker {marker!r}"


def test_dashboard_translation_key_sets_match() -> None:
    de = json.loads(DE.read_text(encoding="utf-8"))
    en = json.loads(EN.read_text(encoding="utf-8"))
    assert set(de) == set(en)


def test_dashboard_shell_exposes_language_theme_and_state_contracts() -> None:
    html = TEMPLATE.read_text(encoding="utf-8")
    assert 'name="viewport"' in html
    assert 'data-dashboard-shell="loading"' in html
    assert 'id="dashboard-language-toggle"' in html
    assert 'id="dashboard-dark-toggle"' in html
    assert 'id="global-notification-area"' in html
    assert 'class="locked-region"' in html
    assert 'id="issues-locked-note"' in html
    assert 'id="reports-locked-note"' in html
    assert 'class="empty-state executive-empty"' in html


def test_dashboard_styles_include_dark_and_responsive_contracts() -> None:
    css = STYLE.read_text(encoding="utf-8")
    assert "dark-mode" in css
    assert "@media (max-width: 900px)" in css
    assert "@media (max-width: 720px)" in css


def test_executive_report_has_print_viewport_and_two_page_contract() -> None:
    html = REPORT.read_text(encoding="utf-8")
    assert 'name="viewport"' in html
    assert html.count('class="report-page') == 2
    assert "money-long" in html
    assert "exception-note" in html
