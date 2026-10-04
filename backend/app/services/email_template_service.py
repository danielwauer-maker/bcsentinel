from __future__ import annotations

import re
from collections.abc import Mapping

from sqlalchemy import select

from app.models import AdminEmailTemplate
from app.services.billing_service import utc_now

PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")

DEFAULT_ADMIN_EMAIL_TEMPLATES: dict[str, dict[str, object]] = {
    "partner_access_invite": {
        "label": "Partner access invite",
        "description": "Wird versendet, wenn eine Partner-Bewerbung im Admin auf accepted gesetzt wird.",
        "placeholders": ["contact_name", "reset_url"],
        "subject": "Your BCSentinel partner access is ready",
        "html": """
<html>
  <body style="font-family: Arial, sans-serif; color: #1f2a44;">
    <p>Hello {{ contact_name }},</p>
    <p>your partner application has been approved.</p>
    <p>Please set your password using this secure link:</p>
    <p><a href="{{ reset_url }}">{{ reset_url }}</a></p>
    <p>After setting your password, you can log in to the partner portal.</p>
  </body>
</html>
""".strip(),
    },
    "partner_reset_request": {
        "label": "Partner password reset",
        "description": "Wird bei Passwort-vergessen an aktive Partner versendet.",
        "placeholders": ["reset_url"],
        "subject": "Reset your BCSentinel partner password",
        "html": """
<html>
  <body style="font-family: Arial, sans-serif; color: #1f2a44;">
    <p>Hello,</p>
    <p>we received a request to reset your BCSentinel partner password.</p>
    <p><a href="{{ reset_url }}">Reset password</a></p>
    <p>If you did not request this, you can ignore this email.</p>
    <p>Link expires automatically.</p>
  </body>
</html>
""".strip(),
    },
    "partner_application_received": {
        "label": "Partner registration received",
        "description": "Wird direkt nach der öffentlichen Partner-Registrierung versendet.",
        "placeholders": ["contact_name"],
        "subject": "We received your BCSentinel partner application",
        "html": """
<html>
  <body style="font-family: Arial, sans-serif; color: #1f2a44;">
    <p>Hello {{ contact_name }},</p>
    <p>thank you for your partner registration at BCSentinel.</p>
    <p>We will review your application and send your portal access as soon as it is approved.</p>
  </body>
</html>
""".strip(),
    },
    "dashboard_access_invite_en": {
        "label": "Dashboard access invite EN",
        "description": "Sent after Business Central tenant registration to invite the dashboard contact.",
        "placeholders": ["dashboard_url", "login_email", "tenant_id", "support_email"],
        "subject": "Your BCSentinel Dashboard access",
        "html": """
<html>
  <body style="font-family: Arial, sans-serif; color: #1f2a44;">
    <p>Hello,</p>
    <p>Your BCSentinel tenant was registered successfully. Dashboard access has been prepared for this email address.</p>
    <p><strong>Dashboard:</strong> <a href="{{ dashboard_url }}">{{ dashboard_url }}</a></p>
    <p><strong>Login email:</strong> {{ login_email }}</p>
    <p>This access is bound to tenant <strong>{{ tenant_id }}</strong>.</p>
    <p>Use the secure activation link above to choose your password. Afterwards you can sign in directly to the BCSentinel Dashboard.</p>
    <p>For support, contact <a href="mailto:{{ support_email }}">{{ support_email }}</a>.</p>
  </body>
</html>
""".strip(),
    },
    "dashboard_password_reset_en": {
        "label": "Dashboard password reset EN",
        "description": "Sent after a dashboard password reset request.",
        "placeholders": ["reset_url", "support_email"],
        "subject": "Reset your BCSentinel Dashboard password",
        "html": """
<html>
  <body style="font-family: Arial, sans-serif; color: #1f2a44;">
    <p>Hello,</p>
    <p>we received a request to reset your BCSentinel Dashboard password.</p>
    <p><a href="{{ reset_url }}">Reset password</a></p>
    <p>This link expires automatically and can only be used once.</p>
    <p>If you did not request this, ignore this message or contact {{ support_email }}.</p>
  </body>
</html>
""".strip(),
    },
    "dashboard_password_reset_de": {
        "label": "Dashboard password reset DE",
        "description": "Wird nach einer Passwort-Reset-Anfrage fuer das Dashboard versendet.",
        "placeholders": ["reset_url", "support_email"],
        "subject": "BCSentinel Dashboard-Kennwort zuruecksetzen",
        "html": """
<html>
  <body style="font-family: Arial, sans-serif; color: #1f2a44;">
    <p>Hallo,</p>
    <p>wir haben eine Anfrage zum Zuruecksetzen Ihres BCSentinel Dashboard-Kennworts erhalten.</p>
    <p><a href="{{ reset_url }}">Kennwort zuruecksetzen</a></p>
    <p>Der Link laeuft automatisch ab und kann nur einmal verwendet werden.</p>
    <p>Falls Sie die Anfrage nicht gestellt haben, ignorieren Sie diese Nachricht oder kontaktieren Sie {{ support_email }}.</p>
  </body>
</html>
""".strip(),
    },
    "dashboard_welcome_en": {
        "label": "Dashboard welcome EN",
        "description": "Sent once after successful dashboard activation.",
        "placeholders": ["dashboard_url", "support_email"],
        "subject": "Welcome to BCSentinel",
        "html": """
<html>
  <body style="font-family: Arial, sans-serif; color: #1f2a44; line-height: 1.5;">
    <p>Hello,</p>
    <h2>Welcome to BCSentinel.</h2>
    <p>Your Dashboard access is active. You can now review your Data Health Score, findings and Executive Reports according to your current product access.</p>
    <p><a href="{{ dashboard_url }}">Open BCSentinel Dashboard</a></p>
    <p>If you need help during the pilot, contact <a href="mailto:{{ support_email }}">{{ support_email }}</a>.</p>
    <p>BCSentinel · Data Quality. Measurable Impact.</p>
  </body>
</html>
""".strip(),
    },
    "dashboard_welcome_de": {
        "label": "Dashboard welcome DE",
        "description": "Wird einmalig nach erfolgreicher Dashboard-Aktivierung versendet.",
        "placeholders": ["dashboard_url", "support_email"],
        "subject": "Willkommen bei BCSentinel",
        "html": """
<html>
  <body style="font-family: Arial, sans-serif; color: #1f2a44; line-height: 1.5;">
    <p>Hallo,</p>
    <h2>Willkommen bei BCSentinel.</h2>
    <p>Ihr Dashboard-Zugang ist aktiv. Sie koennen jetzt – entsprechend Ihrem aktuellen Produktzugang – Data Health Score, Findings und Executive Reports einsehen.</p>
    <p><a href="{{ dashboard_url }}">BCSentinel Dashboard oeffnen</a></p>
    <p>Wenn Sie waehrend des Piloten Unterstuetzung benoetigen, schreiben Sie an <a href="mailto:{{ support_email }}">{{ support_email }}</a>.</p>
    <p>BCSentinel · Data Quality. Measurable Impact.</p>
  </body>
</html>
""".strip(),
    },
    "dashboard_access_invite_de": {
        "label": "Dashboard access invite DE",
        "description": "Wird nach der Business-Central-Tenant-Registrierung an den Dashboard-Kontakt versendet.",
        "placeholders": ["dashboard_url", "login_email", "tenant_id", "support_email"],
        "subject": "Ihr BCSentinel Dashboard-Zugang",
        "html": """
<html>
  <body style="font-family: Arial, sans-serif; color: #1f2a44;">
    <p>Hallo,</p>
    <p>Ihr BCSentinel Tenant wurde erfolgreich registriert. Der Dashboard-Zugang wurde fuer diese E-Mail-Adresse vorbereitet.</p>
    <p><strong>Dashboard:</strong> <a href="{{ dashboard_url }}">{{ dashboard_url }}</a></p>
    <p><strong>Login-E-Mail:</strong> {{ login_email }}</p>
    <p>Dieser Zugriff ist an Tenant <strong>{{ tenant_id }}</strong> gebunden.</p>
    <p>Waehlen Sie ueber den sicheren Aktivierungslink oben Ihr Kennwort. Anschliessend koennen Sie sich direkt am BCSentinel Dashboard anmelden.</p>
    <p>Support: <a href="mailto:{{ support_email }}">{{ support_email }}</a>.</p>
  </body>
</html>
""".strip(),
    },
}


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
    row = db.get(AdminEmailTemplate, key)
    if row is None:
        raise KeyError(key)
    row.subject_template = subject_template.strip()
    row.html_template = html_template.strip()
    row.updated_at_utc = utc_now()
    db.commit()
    db.refresh(row)
    return row


def render_email_template(db, key: str, context: Mapping[str, object] | None = None) -> tuple[str, str]:
    ensure_default_email_templates(db)
    row = db.get(AdminEmailTemplate, key)
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
