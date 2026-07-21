from sqlalchemy import func, select

from app.models import CheckDefinition, CheckTranslation
from app.services.check_catalog_service import (
    ensure_default_check_catalog,
    load_default_catalog,
    resolve_check_text,
    restore_standard_texts,
    update_check_translation,
    validate_default_catalog,
)
from app.services.issue_text_service import issue_text
from app.services.scoring_service import QUICK_CHECKS, calculate_quick_scan_result


def _seed(db_session) -> None:
    ensure_default_check_catalog(db_session)
    db_session.commit()


def test_default_catalog_has_unique_ids_and_complete_required_translations() -> None:
    defaults = load_default_catalog()
    validate_default_catalog(defaults)
    assert len(defaults) == len({item["check_id"] for item in defaults})
    assert {check.code for check in QUICK_CHECKS}.issubset({item["check_id"] for item in defaults})


def test_seed_creates_every_check_and_both_required_languages(db_session) -> None:
    _seed(db_session)
    assert db_session.scalar(select(func.count(CheckDefinition.check_id))) == len(load_default_catalog())
    assert db_session.scalar(select(func.count(CheckTranslation.check_id))) == 2 * len(load_default_catalog())
    assert db_session.scalar(select(func.count(CheckTranslation.check_id)).where(CheckTranslation.title == "")) == 0


def test_issue_text_uses_exact_fallback_order(db_session) -> None:
    _seed(db_session)
    code = "CUSTOMERS_MISSING_POSTCODE"
    assert issue_text(db_session, code, "de-DE").title == "Debitoren ohne Postleitzahl"
    assert issue_text(db_session, code, "fr-FR").title == "Debitoren ohne Postleitzahl"

    german = db_session.get(CheckTranslation, (code, "de-DE"))
    german.title = ""
    assert resolve_check_text(db_session, code, "fr-FR").title == "Customers without a post code"
    english = db_session.get(CheckTranslation, (code, "en-US"))
    english.title = ""
    assert resolve_check_text(db_session, code, "fr-FR").title == code


def test_customer_override_survives_upgrade_and_can_be_restored(db_session) -> None:
    _seed(db_session)
    code = "CUSTOMERS_MISSING_POSTCODE"
    update_check_translation(
        db_session, code, "de-DE", title="Kundentitel",
        short_description="Kundenspezifische Kurzbeschreibung.",
        recommendation="Kundenspezifische Empfehlung.",
    )
    ensure_default_check_catalog(db_session)
    assert db_session.get(CheckTranslation, (code, "de-DE")).title == "Kundentitel"

    restore_standard_texts(db_session, code)
    restored = db_session.get(CheckTranslation, (code, "de-DE"))
    assert restored.title == "Debitoren ohne Postleitzahl"
    assert restored.is_customized is False


def test_quick_scan_renders_catalog_texts_in_requested_language(db_session) -> None:
    _seed(db_session)
    metrics = {"customers_total": 10, "customers_missing_postcode": 1}
    english = calculate_quick_scan_result(db_session, metrics, "en-US")
    german = calculate_quick_scan_result(db_session, metrics, "de-DE")
    assert english[4][0].code == german[4][0].code == "CUSTOMERS_MISSING_POSTCODE"
    assert english[4][0].title == "Customers without a post code"
    assert german[4][0].title == "Debitoren ohne Postleitzahl"
    assert english[4][0].recommendation_preview != german[4][0].recommendation_preview


def test_authenticated_catalog_api_returns_runtime_texts(client, tenant_factory, auth_header_factory) -> None:
    tenant = tenant_factory()
    response = client.get(
        "/catalog/checks?language=de-DE",
        headers=auth_header_factory(tenant),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["fallback_order"] == ["de-DE", "en-US", "check_id"]
    by_id = {item["check_id"]: item for item in payload["checks"]}
    assert by_id["CUSTOMERS_MISSING_POSTCODE"]["title"] == "Debitoren ohne Postleitzahl"
    assert by_id["CUSTOMERS_MISSING_POSTCODE"]["recommendation"]
