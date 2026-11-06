from __future__ import annotations

import pytest

from app.db import SessionLocal
from app.models import AdminEmailTemplate
from app.services.email_template_service import (
    ensure_default_email_templates,
    list_email_templates_for_admin,
    render_email_template,
    storage_key,
    update_email_template,
)


def test_default_catalog_seeds_english_and_german_variants():
    with SessionLocal() as db:
        ensure_default_email_templates(db)
        rows = {row.key for row in db.query(AdminEmailTemplate).all()}
        assert "partner_access_invite" in rows
        assert "partner_access_invite_de" in rows
        templates = list_email_templates_for_admin(db)
        languages = {(item["base_key"], item["language"]) for item in templates}
        assert ("partner_access_invite", "en") in languages
        assert ("partner_access_invite", "de") in languages


def test_render_selects_german_and_keeps_english_fallback():
    with SessionLocal() as db:
        de_subject, de_html = render_email_template(
            db,
            "partner_access_invite",
            {"contact_name": "Daniel", "reset_url": "https://example.invalid/reset"},
            language="de-DE",
        )
        en_subject, _ = render_email_template(
            db,
            "partner_access_invite",
            {"contact_name": "Daniel", "reset_url": "https://example.invalid/reset"},
            language="fr",
        )
    assert "Partnerzugang" in de_subject
    assert "Hallo Daniel" in de_html
    assert en_subject == "Your BCSentinel partner access is ready"


def test_admin_editing_preserves_language_record_and_rejects_unsafe_content():
    with SessionLocal() as db:
        ensure_default_email_templates(db)
        key = storage_key("partner_reset_request", "de")
        row = update_email_template(
            db,
            key=key,
            subject_template="Neues Passwort",
            html_template='<p><a href="{{ reset_url }}">Passwort setzen</a></p>',
        )
        assert row.key == "partner_reset_request_de"
        assert row.subject_template == "Neues Passwort"

        with pytest.raises(ValueError):
            update_email_template(
                db,
                key=key,
                subject_template="Unsafe {{ unknown_value }}",
                html_template="<script>alert(1)</script>",
            )
