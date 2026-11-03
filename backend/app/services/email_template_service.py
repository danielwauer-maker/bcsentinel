from __future__ import annotations

import re
from collections.abc import Mapping

from sqlalchemy import select

from app.models import AdminEmailTemplate
from app.services.billing_service import utc_now

PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")
SUPPORTED_EMAIL_LANGUAGES = ("en", "de")


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

BASE_TEMPLATE_META.update({
    "lifecycle_registration_completed": {
        "label": "Lifecycle · Registration completed",
        "description": "Transactional lifecycle email after BCSentinel tenant registration.",
        "placeholders": ["environment_name"],
        "translations": {
            "en": {"subject": "BCSentinel registration completed", "html": "<p>Your BCSentinel registration is complete. You can now start your first Data Health Scan.</p>"},
            "de": {"subject": "BCSentinel Registrierung abgeschlossen", "html": "<p>Ihre BCSentinel-Registrierung ist abgeschlossen. Sie können jetzt Ihren ersten Data Health Scan starten.</p>"},
        },
    },
    "lifecycle_scan_started": {
        "label": "Lifecycle · Scan started",
        "description": "Transactional lifecycle email when a Data Health Scan starts.",
        "placeholders": ["scan_id"],
        "translations": {
            "en": {"subject": "BCSentinel scan started", "html": "<p>Your Data Health Scan <strong>{{ scan_id }}</strong> has started. You will receive another message when the result is available.</p>"},
            "de": {"subject": "BCSentinel Scan gestartet", "html": "<p>Ihr Data Health Scan <strong>{{ scan_id }}</strong> wurde gestartet. Sie erhalten eine weitere Nachricht, sobald das Ergebnis verfügbar ist.</p>"},
        },
    },
    "lifecycle_scan_completed": {
        "label": "Lifecycle · Scan completed",
        "description": "Transactional lifecycle email for a completed non-validation scan. Fiverr next-purchase guidance is appended separately.",
        "placeholders": ["scan_id", "data_score", "report_url"],
        "translations": {
            "en": {"subject": "BCSentinel scan completed", "html": "<p>Scan <strong>{{ scan_id }}</strong> is complete. Data Health Score: <strong>{{ data_score }}/100</strong>.</p><p><a href=\"{{ report_url }}\">Open BCSentinel report</a></p>"},
            "de": {"subject": "BCSentinel Scan abgeschlossen", "html": "<p>Der Scan <strong>{{ scan_id }}</strong> ist abgeschlossen. Data Health Score: <strong>{{ data_score }}/100</strong>.</p><p><a href=\"{{ report_url }}\">BCSentinel Report öffnen</a></p>"},
        },
    },
    "lifecycle_scan_failed": {
        "label": "Lifecycle · Scan failed",
        "description": "Transactional lifecycle email for a failed scan.",
        "placeholders": ["scan_id", "error_message"],
        "translations": {
            "en": {"subject": "BCSentinel scan failed", "html": "<p>Scan <strong>{{ scan_id }}</strong> could not be completed. {{ error_message }}</p>"},
            "de": {"subject": "BCSentinel Scan fehlgeschlagen", "html": "<p>Der Scan <strong>{{ scan_id }}</strong> konnte nicht abgeschlossen werden. {{ error_message }}</p>"},
        },
    },
    "lifecycle_quick_activated_existing": {
        "label": "Lifecycle · Quick activated · existing scan",
        "description": "Permanent Quick activation when a qualifying scan already exists.",
        "placeholders": ["report_url"],
        "translations": {
            "en": {"subject": "BCSentinel Quick Assessment activated", "html": "<p>Your Quick Assessment is permanently unlocked for the existing Data Health Scan. You can reopen the prioritized Quick Assessment results through BCSentinel at any time.</p><p><a href=\"{{ report_url }}\">Open BCSentinel report</a></p>"},
            "de": {"subject": "BCSentinel Quick Assessment aktiviert", "html": "<p>Ihr Quick Assessment ist dauerhaft für den vorhandenen Data Health Scan freigeschaltet. Sie können die priorisierten Quick-Assessment-Ergebnisse jederzeit erneut über BCSentinel öffnen.</p><p><a href=\"{{ report_url }}\">BCSentinel Report öffnen</a></p>"},
        },
    },
    "lifecycle_quick_activated_prescan": {
        "label": "Lifecycle · Quick activated · before first scan",
        "description": "Permanent Quick activation before the first qualifying scan.",
        "placeholders": [],
        "translations": {
            "en": {"subject": "BCSentinel Quick Assessment activated", "html": "<p>Your Quick Assessment is permanently unlocked. Start the included first Data Health Scan; once it completes, the Quick Assessment Report for that scan will become available automatically.</p>"},
            "de": {"subject": "BCSentinel Quick Assessment aktiviert", "html": "<p>Ihr Quick Assessment ist dauerhaft freigeschaltet. Starten Sie jetzt den enthaltenen ersten Data Health Scan; nach Abschluss wird automatisch der Quick Assessment Report für diesen Scan verfügbar.</p>"},
        },
    },
    "lifecycle_quick_activated_legacy": {
        "label": "Lifecycle · Quick activated · legacy finite",
        "description": "Compatibility template for historical finite Quick grants only.",
        "placeholders": ["valid_until", "report_url"],
        "translations": {
            "en": {"subject": "BCSentinel Quick Assessment activated", "html": "<p>Your Quick Assessment is active until <strong>{{ valid_until }}</strong>. You can now review the prioritized Quick Assessment results from your existing Data Health Scan.</p><p><a href=\"{{ report_url }}\">Open BCSentinel report</a></p>"},
            "de": {"subject": "BCSentinel Quick Assessment aktiviert", "html": "<p>Ihr Quick Assessment ist bis <strong>{{ valid_until }}</strong> aktiv. Sie können jetzt die priorisierten Quick-Assessment-Ergebnisse des vorhandenen Data Health Scans einsehen.</p><p><a href=\"{{ report_url }}\">BCSentinel Report öffnen</a></p>"},
        },
    },
    "lifecycle_quick_expiring": {
        "label": "Lifecycle · Quick expiring · legacy",
        "description": "Compatibility template for historical finite Quick grants only.",
        "placeholders": ["valid_until", "report_url"],
        "translations": {
            "en": {"subject": "BCSentinel Quick Assessment: access expires soon", "html": "<p>Your historical time-limited Quick Assessment access expires at <strong>{{ valid_until }}</strong>.</p><p><a href=\"{{ report_url }}\">Open BCSentinel report</a></p>"},
            "de": {"subject": "BCSentinel Quick Assessment: Zugang läuft bald ab", "html": "<p>Ihr historischer zeitlich begrenzter Quick-Assessment-Zugang läuft am <strong>{{ valid_until }}</strong> ab.</p><p><a href=\"{{ report_url }}\">BCSentinel Report öffnen</a></p>"},
        },
    },
    "lifecycle_quick_expired": {
        "label": "Lifecycle · Quick expired · legacy",
        "description": "Compatibility template for historical finite Quick grants only.",
        "placeholders": [],
        "translations": {
            "en": {"subject": "BCSentinel Quick Assessment access expired", "html": "<p>The historical time-limited Quick Assessment access has expired. New Quick Assessments are granted permanently.</p>"},
            "de": {"subject": "BCSentinel Quick-Assessment-Zugang abgelaufen", "html": "<p>Der historische zeitlich begrenzte Quick-Assessment-Zugang ist abgelaufen. Neue Quick Assessments werden dauerhaft freigeschaltet.</p>"},
        },
    },
    "lifecycle_assessment_activated": {
        "label": "Lifecycle · Full Assessment activated",
        "description": "Transactional lifecycle email when Full Assessment detail access is activated.",
        "placeholders": ["valid_until", "report_url"],
        "translations": {
            "en": {"subject": "BCSentinel Assessment activated", "html": "<p>Your full Assessment access is active until <strong>{{ valid_until }}</strong>.</p><p><a href=\"{{ report_url }}\">Open BCSentinel report</a></p>"},
            "de": {"subject": "BCSentinel Assessment aktiviert", "html": "<p>Ihr vollständiger Assessment-Zugang ist bis <strong>{{ valid_until }}</strong> aktiv.</p><p><a href=\"{{ report_url }}\">BCSentinel Report öffnen</a></p>"},
        },
    },
    "lifecycle_assessment_extended": {
        "label": "Lifecycle · Full Assessment extended",
        "description": "Transactional lifecycle email after the one allowed Full Assessment extension.",
        "placeholders": ["valid_until", "report_url"],
        "translations": {
            "en": {"subject": "BCSentinel Assessment extended", "html": "<p>Your full Assessment access is active until <strong>{{ valid_until }}</strong>.</p><p><a href=\"{{ report_url }}\">Open BCSentinel report</a></p>"},
            "de": {"subject": "BCSentinel Assessment verlängert", "html": "<p>Ihr vollständiger Assessment-Zugang ist bis <strong>{{ valid_until }}</strong> aktiv.</p><p><a href=\"{{ report_url }}\">BCSentinel Report öffnen</a></p>"},
        },
    },
    "lifecycle_assessment_expiring": {
        "label": "Lifecycle · Full Assessment expiring",
        "description": "Transactional warning before Full Assessment detail access expires.",
        "placeholders": ["valid_until"],
        "translations": {
            "en": {"subject": "BCSentinel Assessment: access expires soon", "html": "<p>Your Assessment access expires at <strong>{{ valid_until }}</strong>. Download your report and plan next steps if needed.</p>"},
            "de": {"subject": "BCSentinel Assessment: Zugang läuft bald ab", "html": "<p>Ihr Assessment-Zugang läuft am <strong>{{ valid_until }}</strong> ab. Laden Sie Ihren Report herunter und planen Sie bei Bedarf die nächsten Schritte.</p>"},
        },
    },
    "lifecycle_assessment_expired": {
        "label": "Lifecycle · Full Assessment expired",
        "description": "Transactional email after Full Assessment detail access expires.",
        "placeholders": [],
        "translations": {
            "en": {"subject": "BCSentinel Assessment access expired", "html": "<p>Live access to full Assessment details has expired. Any permanently purchased Quick Assessment remains available.</p>"},
            "de": {"subject": "BCSentinel Assessment-Zugang abgelaufen", "html": "<p>Der Live-Zugriff auf die vollständigen Assessment-Details ist abgelaufen. Ein dauerhaft erworbenes Quick Assessment bleibt davon unberührt.</p>"},
        },
    },
    "lifecycle_validation_available": {
        "label": "Lifecycle · Validation available",
        "description": "Transactional lifecycle email after Validation is granted and before the new scan.",
        "placeholders": ["baseline_scan_id"],
        "translations": {
            "en": {"subject": "BCSentinel Validation available", "html": "<p>Your Validation is available. Start a new Data Health Scan now. The 7-day full Validation result window begins with that new scan.</p><p>Baseline: <strong>{{ baseline_scan_id }}</strong></p>"},
            "de": {"subject": "BCSentinel Validation verfügbar", "html": "<p>Ihre Validation ist freigeschaltet. Starten Sie jetzt einen neuen Data Health Scan. Das 7-Tage-Fenster für vollständige Validation-Ergebnisse beginnt mit diesem neuen Scan.</p><p>Baseline: <strong>{{ baseline_scan_id }}</strong></p>"},
        },
    },
    "lifecycle_validation_completed": {
        "label": "Lifecycle · Validation completed",
        "description": "Transactional lifecycle email after the Validation scan completes.",
        "placeholders": ["scan_id", "data_score", "report_url"],
        "translations": {
            "en": {"subject": "BCSentinel validation completed", "html": "<p>Scan <strong>{{ scan_id }}</strong> is complete. Data Health Score: <strong>{{ data_score }}/100</strong>.</p><p><a href=\"{{ report_url }}\">Open BCSentinel report</a></p>"},
            "de": {"subject": "BCSentinel Validation abgeschlossen", "html": "<p>Der Scan <strong>{{ scan_id }}</strong> ist abgeschlossen. Data Health Score: <strong>{{ data_score }}/100</strong>.</p><p><a href=\"{{ report_url }}\">BCSentinel Report öffnen</a></p>"},
        },
    },
    "lifecycle_validation_expiring": {
        "label": "Lifecycle · Validation expiring",
        "description": "Transactional warning before Validation result access expires.",
        "placeholders": ["valid_until"],
        "translations": {
            "en": {"subject": "BCSentinel Validation: access expires soon", "html": "<p>Your Validation access expires at <strong>{{ valid_until }}</strong>. Download your report and plan next steps if needed.</p>"},
            "de": {"subject": "BCSentinel Validation: Zugang läuft bald ab", "html": "<p>Ihr Validation-Zugang läuft am <strong>{{ valid_until }}</strong> ab. Laden Sie Ihren Report herunter und planen Sie bei Bedarf die nächsten Schritte.</p>"},
        },
    },
})


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