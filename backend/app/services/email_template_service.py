from __future__ import annotations

import re
from collections.abc import Mapping

from sqlalchemy import select

from app.models import AdminEmailTemplate
from app.services.billing_service import utc_now

PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")
SUPPORTED_EMAIL_LANGUAGES = ("en", "de")

# English keeps the historical storage key for backward compatibility. Localized
# variants use a deterministic suffix and therefore need no schema migration.
def storage_key(base_key: str, language: str = "en") -> str:
    normalized_language = (language or "en").strip().lower()
    if normalized_language not in SUPPORTED_EMAIL_LANGUAGES:
        normalized_language = "en"
    return base_key if normalized_language == "en" else f"{base_key}_{normalized_language}"


BASE_TEMPLATE_META: dict[str, dict[str, object]] = {
    "partner_access_invite": {
        "label": "Partner access invite",
        "description": "Wird versendet, wenn eine Partner-Bewerbung im Admin auf accepted gesetzt wird.",
        "placeholders": ["contact_name", "reset_url"],
        "translations": {
            "en": {
                "subject": "Your BCSentinel partner access is ready",
                "html": """
<html><body style="font-family: Arial, sans-serif; color: #1f2a44;">
<p>Hello {{ contact_name }},</p><p>your partner application has been approved.</p>
<p>Please set your password using this secure link:</p><p><a href="{{ reset_url }}">{{ reset_url }}</a></p>
<p>After setting your password, you can log in to the partner portal.</p>
</body></html>""".strip(),
            },
            "de": {
                "subject": "Ihr BCSentinel-Partnerzugang ist bereit",
                "html": """
<html><body style="font-family: Arial, sans-serif; color: #1f2a44;">
<p>Hallo {{ contact_name }},</p><p>Ihre Partner-Bewerbung wurde freigegeben.</p>
<p>Bitte legen Sie Ihr Passwort über diesen sicheren Link fest:</p><p><a href="{{ reset_url }}">{{ reset_url }}</a></p>
<p>Anschließend können Sie sich im Partnerportal anmelden.</p>
</body></html>""".strip(),
            },
        },
    },
    "partner_reset_request": {
        "label": "Partner password reset",
        "description": "Wird bei Passwort-vergessen an aktive Partner versendet.",
        "placeholders": ["reset_url"],
        "translations": {
            "en": {
                "subject": "Reset your BCSentinel partner password",
                "html": """
<html><body style="font-family: Arial, sans-serif; color: #1f2a44;">
<p>Hello,</p><p>we received a request to reset your BCSentinel partner password.</p>
<p><a href="{{ reset_url }}">Reset password</a></p><p>If you did not request this, you can ignore this email.</p>
<p>Link expires automatically.</p></body></html>""".strip(),
            },
            "de": {
                "subject": "BCSentinel-Partnerpasswort zurücksetzen",
                "html": """
<html><body style="font-family: Arial, sans-serif; color: #1f2a44;">
<p>Hallo,</p><p>wir haben eine Anfrage zum Zurücksetzen Ihres BCSentinel-Partnerpassworts erhalten.</p>
<p><a href="{{ reset_url }}">Passwort zurücksetzen</a></p><p>Wenn Sie dies nicht angefordert haben, können Sie diese E-Mail ignorieren.</p>
<p>Der Link läuft automatisch ab.</p></body></html>""".strip(),
            },
        },
    },
    "partner_application_received": {
        "label": "Partner registration received",
        "description": "Wird direkt nach der öffentlichen Partner-Registrierung versendet.",
        "placeholders": ["contact_name"],
        "translations": {
            "en": {
                "subject": "We received your BCSentinel partner application",
                "html": """
<html><body style="font-family: Arial, sans-serif; color: #1f2a44;">
<p>Hello {{ contact_name }},</p><p>thank you for your partner registration at BCSentinel.</p>
<p>We will review your application and send your portal access as soon as it is approved.</p>
</body></html>""".strip(),
            },
            "de": {
                "subject": "Wir haben Ihre BCSentinel-Partnerbewerbung erhalten",
                "html": """
<html><body style="font-family: Arial, sans-serif; color: #1f2a44;">
<p>Hallo {{ contact_name }},</p><p>vielen Dank für Ihre Partnerregistrierung bei BCSentinel.</p>
<p>Wir prüfen Ihre Bewerbung und senden Ihnen den Portalzugang nach der Freigabe zu.</p>
</body></html>""".strip(),
            },
        },
    },
}


# Admin surfaces historically import this symbol. Keep it as a flat storage-key
# catalog while attaching base_key/language metadata to every entry.
DEFAULT_ADMIN_EMAIL_TEMPLATES: dict[str, dict[str, object]] = {}
for _base_key, _meta in BASE_TEMPLATE_META.items():
    for _language in SUPPORTED_EMAIL_LANGUAGES:
        _translation = dict(_meta["translations"][_language])
        DEFAULT_ADMIN_EMAIL_TEMPLATES[storage_key(_base_key, _language)] = {
            "base_key": _base_key,
            "language": _language,
            "label": f"{_meta['label']} ({_language.upper()})",
            "description": _meta["description"],
            "placeholders": list(_meta["placeholders"]),
            "subject": _translation["subject"],
            "html": _translation["html"],
        }


def _normalize_language(language: str | None) -> str:
    normalized = (language or "en").strip().lower().replace("_", "-")
    normalized = normalized.split("-", 1)[0]
    return normalized if normalized in SUPPORTED_EMAIL_LANGUAGES else "en"


def _validate_template_content(base_key: str, subject_template: str, html_template: str) -> None:
    meta = BASE_TEMPLATE_META.get(base_key)
    if meta is None:
        raise KeyError(base_key)
    allowed = set(str(value) for value in meta["placeholders"])
    used = set(PLACEHOLDER_PATTERN.findall(subject_template or "")) | set(PLACEHOLDER_PATTERN.findall(html_template or ""))
    unknown = sorted(used - allowed)
    if unknown:
        raise ValueError(f"Unsupported placeholders for {base_key}: {', '.join(unknown)}")
    lowered = (html_template or "").lower()
    if "<script" in lowered or "javascript:" in lowered:
        raise ValueError("Unsafe active content is not allowed in email templates.")


def ensure_default_email_templates(db) -> None:
    existing = {row.key: row for row in db.scalars(select(AdminEmailTemplate)).all()}
    changed = False
    for key, default in DEFAULT_ADMIN_EMAIL_TEMPLATES.items():
        if key in existing:
            continue
        db.add(
            AdminEmailTemplate(
                key=key,
                subject_template=str(default["subject"]),
                html_template=str(default["html"]),
                updated_at_utc=utc_now(),
            )
        )
        changed = True
    if changed:
        db.commit()


def list_email_templates_for_admin(db) -> list[dict[str, object]]:
    ensure_default_email_templates(db)
    rows = {
        row.key: row
        for row in db.scalars(select(AdminEmailTemplate).order_by(AdminEmailTemplate.key.asc())).all()
    }
    result: list[dict[str, object]] = []
    for key, meta in DEFAULT_ADMIN_EMAIL_TEMPLATES.items():
        row = rows[key]
        result.append(
            {
                "key": key,
                "base_key": meta["base_key"],
                "language": meta["language"],
                "label": meta["label"],
                "description": meta["description"],
                "placeholders": list(meta["placeholders"]),
                "subject_template": row.subject_template,
                "html_template": row.html_template,
                "updated_at_utc": row.updated_at_utc,
            }
        )
    return result


def update_email_template(db, *, key: str, subject_template: str, html_template: str) -> AdminEmailTemplate:
    ensure_default_email_templates(db)
    meta = DEFAULT_ADMIN_EMAIL_TEMPLATES.get(key)
    if meta is None:
        raise KeyError(key)
    _validate_template_content(str(meta["base_key"]), subject_template, html_template)
    row = db.get(AdminEmailTemplate, key)
    if row is None:
        raise KeyError(key)
    row.subject_template = subject_template.strip()
    row.html_template = html_template.strip()
    row.updated_at_utc = utc_now()
    db.commit()
    db.refresh(row)
    return row


def render_email_template(
    db,
    key: str,
    context: Mapping[str, object] | None = None,
    *,
    language: str = "en",
) -> tuple[str, str]:
    ensure_default_email_templates(db)
    normalized_language = _normalize_language(language)
    resolved_key = storage_key(key, normalized_language)
    row = db.get(AdminEmailTemplate, resolved_key)
    if row is None and normalized_language != "en":
        row = db.get(AdminEmailTemplate, storage_key(key, "en"))
    if row is None:
        raise KeyError(key)
    return render_email_template_preview(
        subject_template=row.subject_template,
        html_template=row.html_template,
        context=context,
    )


def render_email_template_preview(
    *,
    subject_template: str,
    html_template: str,
    context: Mapping[str, object] | None = None,
) -> tuple[str, str]:
    values = {str(k): "" if v is None else str(v) for k, v in (context or {}).items()}

    def render(value: str) -> str:
        return PLACEHOLDER_PATTERN.sub(lambda match: values.get(match.group(1), ""), value or "")

    return render(subject_template), render(html_template)
