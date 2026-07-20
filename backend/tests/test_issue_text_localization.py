from app.services.issue_text_service import ISSUE_TEXTS, issue_text
from app.services.scoring_service import QUICK_CHECKS, calculate_quick_scan_result


def test_every_quick_check_has_complete_english_and_german_texts() -> None:
    assert {check.code for check in QUICK_CHECKS} == set(ISSUE_TEXTS)
    for translations in ISSUE_TEXTS.values():
        assert set(translations) == {"en", "de"}
        assert translations["en"].title.strip()
        assert translations["en"].recommendation.strip()
        assert translations["de"].title.strip()
        assert translations["de"].recommendation.strip()


def test_issue_text_uses_stable_code_and_english_fallback() -> None:
    code = "CUSTOMERS_MISSING_POSTCODE"
    assert issue_text(code, "de-DE").title == "Debitoren ohne Postleitzahl"
    assert issue_text(code, "fr-FR").title == "Customers without a post code"


def test_quick_scan_renders_new_findings_in_requested_language() -> None:
    metrics = {"customers_total": 10, "customers_missing_postcode": 1}

    english = calculate_quick_scan_result(metrics, "en-US")
    german = calculate_quick_scan_result(metrics, "de-DE")

    assert english[4][0].code == german[4][0].code == "CUSTOMERS_MISSING_POSTCODE"
    assert english[4][0].title == "Customers without a post code"
    assert german[4][0].title == "Debitoren ohne Postleitzahl"
    assert english[4][0].recommendation_preview != german[4][0].recommendation_preview
