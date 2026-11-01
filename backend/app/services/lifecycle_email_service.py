from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import formataddr
import html
import json
import smtplib
from typing import Any
from urllib.parse import quote

from jose import jwt
from sqlalchemy import select

from app.core.settings import resolve_public_base_url, settings
from app.lifecycle_models import LifecycleEmailOutbox, TenantLifecycleProfile
from app.models import Tenant, TenantProductEntitlement, TenantScanCredit
from app.services.product_license_service import (
    PRODUCT_ASSESSMENT,
    PRODUCT_VALIDATION_CHECK,
    normalize_product_code,
)
from app.services.quick_assessment_access_service import PRODUCT_QUICK_ASSESSMENT

EMAIL_SHARE_ALGORITHM = "HS256"
EMAIL_SHARE_HOURS = 72
MAX_ATTEMPTS = 5
RETRY_MINUTES = 15

EVENT_REGISTRATION_COMPLETED = "registration.completed"
EVENT_SCAN_STARTED = "scan.started"
EVENT_SCAN_COMPLETED = "scan.completed"
EVENT_SCAN_FAILED = "scan.failed"
EVENT_QUICK_ASSESSMENT_ACTIVATED = "quick_assessment.activated"
EVENT_QUICK_ASSESSMENT_EXPIRING = "quick_assessment.expiring"
EVENT_QUICK_ASSESSMENT_EXPIRED = "quick_assessment.expired"
EVENT_ASSESSMENT_ACTIVATED = "assessment.activated"
EVENT_ASSESSMENT_EXPIRING = "assessment.expiring"
EVENT_ASSESSMENT_EXPIRED = "assessment.expired"
EVENT_ASSESSMENT_EXTENDED = "assessment.extended"
EVENT_VALIDATION_AVAILABLE = "validation.available"
EVENT_VALIDATION_COMPLETED = "validation.completed"
EVENT_VALIDATION_EXPIRING = "validation.expiring"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_language(value: str | None) -> str:
    return "de" if (value or "").strip().lower().startswith("de") else "en"


def normalize_email(value: str | None) -> str:
    email = (value or "").strip().lower()
    if not email or "@" not in email or email.startswith("@") or email.endswith("@"):
        raise ValueError("A valid report and notification email is required.")
    if len(email) > 255:
        raise ValueError("The report and notification email is too long.")
    return email


def upsert_lifecycle_profile(
    db,
    *,
    tenant: Tenant,
    email: str,
    language: str | None = None,
) -> TenantLifecycleProfile:
    now = utc_now()
    target_email = normalize_email(email)
    target_language = normalize_language(language or tenant.preferred_language)
    profile = db.get(TenantLifecycleProfile, tenant.tenant_id)
    created = profile is None
    if profile is None:
        profile = TenantLifecycleProfile(
            tenant_id=tenant.tenant_id,
            primary_notification_email=target_email,
            preferred_language=target_language,
            transactional_email_enabled=True,
            created_at_utc=now,
            updated_at_utc=now,
        )
        db.add(profile)
    else:
        profile.primary_notification_email = target_email
        profile.preferred_language = target_language
        profile.transactional_email_enabled = True
        profile.updated_at_utc = now
    db.flush()
    if created:
        queue_lifecycle_email(
            db,
            tenant_id=tenant.tenant_id,
            event_type=EVENT_REGISTRATION_COMPLETED,
            payload={"environment_name": tenant.environment_name or "Business Central"},
            dedupe_key=f"{EVENT_REGISTRATION_COMPLETED}:{tenant.tenant_id}",
        )
    return profile


def _profile(db, tenant_id: str) -> TenantLifecycleProfile | None:
    return db.get(TenantLifecycleProfile, tenant_id)


def queue_lifecycle_email(
    db,
    *,
    tenant_id: str,
    event_type: str,
    payload: dict[str, Any] | None = None,
    dedupe_key: str,
    scheduled_at_utc: datetime | None = None,
) -> LifecycleEmailOutbox | None:
    profile = _profile(db, tenant_id)
    if profile is None or not profile.transactional_email_enabled:
        return None
    existing = db.scalar(select(LifecycleEmailOutbox).where(LifecycleEmailOutbox.dedupe_key == dedupe_key))
    if existing is not None:
        return existing
    now = utc_now()
    row = LifecycleEmailOutbox(
        tenant_id=tenant_id,
        event_type=event_type,
        target_email=profile.primary_notification_email,
        language=normalize_language(profile.preferred_language),
        payload_json=json.dumps(payload or {}, separators=(",", ":"), ensure_ascii=False),
        dedupe_key=dedupe_key,
        status="queued",
        attempts=0,
        scheduled_at_utc=scheduled_at_utc or now,
        sent_at_utc=None,
        last_error=None,
        created_at_utc=now,
        updated_at_utc=now,
    )
    db.add(row)
    db.flush()
    return row


def schedule_entitlement_lifecycle(
    db,
    *,
    tenant_id: str,
    entitlement: TenantProductEntitlement,
    activation_event: str,
    payload: dict[str, Any] | None = None,
) -> None:
    product = normalize_product_code(entitlement.product_code)
    valid_until = entitlement.valid_until_utc
    if valid_until is None:
        return
    if valid_until.tzinfo is None:
        valid_until = valid_until.replace(tzinfo=timezone.utc)
    base_payload = dict(payload or {})
    base_payload["valid_until_utc"] = valid_until.isoformat().replace("+00:00", "Z")
    queue_lifecycle_email(
        db,
        tenant_id=tenant_id,
        event_type=activation_event,
        payload=base_payload,
        dedupe_key=f"{activation_event}:entitlement:{entitlement.id}",
    )
    if product == PRODUCT_QUICK_ASSESSMENT:
        expiring_event, expired_event = EVENT_QUICK_ASSESSMENT_EXPIRING, EVENT_QUICK_ASSESSMENT_EXPIRED
    elif product == PRODUCT_ASSESSMENT:
        expiring_event, expired_event = EVENT_ASSESSMENT_EXPIRING, EVENT_ASSESSMENT_EXPIRED
    elif product == PRODUCT_VALIDATION_CHECK:
        expiring_event, expired_event = EVENT_VALIDATION_EXPIRING, None
    else:
        return
    warning_at = valid_until - timedelta(hours=48)
    if warning_at > utc_now():
        queue_lifecycle_email(
            db,
            tenant_id=tenant_id,
            event_type=expiring_event,
            payload=base_payload,
            dedupe_key=f"{expiring_event}:entitlement:{entitlement.id}",
            scheduled_at_utc=warning_at,
        )
    if expired_event:
        queue_lifecycle_email(
            db,
            tenant_id=tenant_id,
            event_type=expired_event,
            payload=base_payload,
            dedupe_key=f"{expired_event}:entitlement:{entitlement.id}",
            scheduled_at_utc=valid_until,
        )


def _report_token(*, tenant_id: str, scan_id: str, report_type: str, token_type: str) -> str:
    payload = {
        "type": token_type,
        "tenant_id": tenant_id,
        "scan_id": scan_id,
        "report_type": report_type,
        "exp": utc_now() + timedelta(hours=EMAIL_SHARE_HOURS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=EMAIL_SHARE_ALGORITHM)


def quick_assessment_report_link(*, tenant_id: str, scan_id: str) -> str | None:
    base_url = resolve_public_base_url()
    if not base_url:
        return None
    token = _report_token(
        tenant_id=tenant_id,
        scan_id=scan_id,
        report_type="html",
        token_type="quick_assessment_report_share",
    )
    return f"{base_url}/reports/quick-assessment/{quote(scan_id)}/html/shared?token={quote(token)}"


def report_link(db, *, tenant_id: str, scan_id: str) -> str | None:
    base_url = resolve_public_base_url()
    if not base_url:
        return None
    validation_credit = db.scalar(
        select(TenantScanCredit).where(
            TenantScanCredit.tenant_id == tenant_id,
            TenantScanCredit.consumed_scan_id == scan_id,
            TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
            TenantScanCredit.status == "consumed",
        )
    )
    if validation_credit is not None:
        path = "validation"
        token_type = "validation_report_share"
    else:
        assessment_active = db.scalar(
            select(TenantProductEntitlement).where(
                TenantProductEntitlement.tenant_id == tenant_id,
                TenantProductEntitlement.product_code == PRODUCT_ASSESSMENT,
                TenantProductEntitlement.status == "active",
                TenantProductEntitlement.valid_until_utc >= utc_now(),
            ).order_by(TenantProductEntitlement.valid_until_utc.desc())
        )
        if assessment_active is not None:
            path = "assessment"
            token_type = "executive_report_share"
        else:
            path = "free-health"
            token_type = "free_health_report_share"
    token = _report_token(tenant_id=tenant_id, scan_id=scan_id, report_type="html", token_type=token_type)
    return f"{base_url}/reports/{path}/{quote(scan_id)}/html/shared?token={quote(token)}"


def queue_scan_completed(db, *, tenant_id: str, scan_id: str, data_score: int) -> None:
    link = report_link(db, tenant_id=tenant_id, scan_id=scan_id)
    validation_credit = db.scalar(
        select(TenantScanCredit).where(
            TenantScanCredit.tenant_id == tenant_id,
            TenantScanCredit.consumed_scan_id == scan_id,
            TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
            TenantScanCredit.status == "consumed",
        )
    )
    event_type = EVENT_VALIDATION_COMPLETED if validation_credit is not None else EVENT_SCAN_COMPLETED
    queue_lifecycle_email(
        db,
        tenant_id=tenant_id,
        event_type=event_type,
        payload={"scan_id": scan_id, "data_score": int(data_score), "report_url": link or ""},
        dedupe_key=f"{event_type}:{tenant_id}:{scan_id}",
    )


def queue_scan_failed(db, *, tenant_id: str, scan_id: str, error_message: str | None = None) -> None:
    queue_lifecycle_email(
        db,
        tenant_id=tenant_id,
        event_type=EVENT_SCAN_FAILED,
        payload={"scan_id": scan_id, "error_message": (error_message or "")[:300]},
        dedupe_key=f"{EVENT_SCAN_FAILED}:{tenant_id}:{scan_id}",
    )


def _event_copy(event_type: str, language: str, payload: dict[str, Any]) -> tuple[str, str]:
    de = language == "de"
    scan_id = html.escape(str(payload.get("scan_id") or ""))
    report_url = html.escape(str(payload.get("report_url") or ""), quote=True)
    valid_until = html.escape(str(payload.get("valid_until_utc") or ""))
    data_score = html.escape(str(payload.get("data_score") or ""))
    error_message = html.escape(str(payload.get("error_message") or ""))
    link_html = f'<p><a href="{report_url}">BCSentinel Report öffnen</a></p>' if report_url and de else (f'<p><a href="{report_url}">Open BCSentinel report</a></p>' if report_url else "")

    if event_type == EVENT_REGISTRATION_COMPLETED:
        return (
            ("BCSentinel Registrierung abgeschlossen" if de else "BCSentinel registration completed"),
            ("<p>Ihre BCSentinel-Registrierung ist abgeschlossen. Sie können jetzt Ihren ersten Data Health Scan starten.</p>" if de else "<p>Your BCSentinel registration is complete. You can now start your first Data Health Scan.</p>"),
        )
    if event_type in {EVENT_SCAN_COMPLETED, EVENT_VALIDATION_COMPLETED}:
        validation = event_type == EVENT_VALIDATION_COMPLETED
        subject = ("BCSentinel Validation abgeschlossen" if de else "BCSentinel validation completed") if validation else ("BCSentinel Scan abgeschlossen" if de else "BCSentinel scan completed")
        body = (f"<p>Der Scan <strong>{scan_id}</strong> ist abgeschlossen. Data Health Score: <strong>{data_score}/100</strong>.</p>" if de else f"<p>Scan <strong>{scan_id}</strong> is complete. Data Health Score: <strong>{data_score}/100</strong>.</p>")
        return subject, body + link_html
    if event_type == EVENT_SCAN_FAILED:
        return (
            ("BCSentinel Scan fehlgeschlagen" if de else "BCSentinel scan failed"),
            (f"<p>Der Scan <strong>{scan_id}</strong> konnte nicht abgeschlossen werden. {error_message}</p>" if de else f"<p>Scan <strong>{scan_id}</strong> could not be completed. {error_message}</p>"),
        )
    if event_type == EVENT_QUICK_ASSESSMENT_ACTIVATED:
        return (
            ("BCSentinel Quick Assessment aktiviert" if de else "BCSentinel Quick Assessment activated"),
            (f"<p>Ihr Quick Assessment ist bis <strong>{valid_until}</strong> aktiv. Sie können jetzt die priorisierten Quick-Assessment-Ergebnisse des vorhandenen Data Health Scans einsehen.</p>" if de else f"<p>Your Quick Assessment is active until <strong>{valid_until}</strong>. You can now review the prioritized Quick Assessment results from your existing Data Health Scan.</p>") + link_html,
        )
    if event_type == EVENT_QUICK_ASSESSMENT_EXPIRING:
        return (
            ("BCSentinel Quick Assessment: Zugang läuft bald ab" if de else "BCSentinel Quick Assessment: access expires soon"),
            (f"<p>Ihr Quick-Assessment-Zugang läuft am <strong>{valid_until}</strong> ab. Öffnen oder speichern Sie Ihren Quick Assessment Report, bevor der Live-Zugriff endet.</p>" if de else f"<p>Your Quick Assessment access expires at <strong>{valid_until}</strong>. Open or save your Quick Assessment Report before live access ends.</p>") + link_html,
        )
    if event_type == EVENT_QUICK_ASSESSMENT_EXPIRED:
        return (
            ("BCSentinel Quick-Assessment-Zugang abgelaufen" if de else "BCSentinel Quick Assessment access expired"),
            ("<p>Der Live-Zugriff auf das Quick Assessment ist abgelaufen. Der gespeicherte Data Health Scan bleibt erhalten und kann weiterhin für ein Full Assessment freigeschaltet werden.</p>" if de else "<p>Live access to the Quick Assessment has expired. The stored Data Health Scan remains available and can still be unlocked with a Full Assessment.</p>"),
        )
    if event_type in {EVENT_ASSESSMENT_ACTIVATED, EVENT_ASSESSMENT_EXTENDED}:
        extended = event_type == EVENT_ASSESSMENT_EXTENDED
        subject = ("BCSentinel Assessment verlängert" if de else "BCSentinel Assessment extended") if extended else ("BCSentinel Assessment aktiviert" if de else "BCSentinel Assessment activated")
        body = (f"<p>Ihr vollständiger Assessment-Zugang ist bis <strong>{valid_until}</strong> aktiv.</p>" if de else f"<p>Your full Assessment access is active until <strong>{valid_until}</strong>.</p>")
        return subject, body + link_html
    if event_type == EVENT_VALIDATION_AVAILABLE:
        return (
            ("BCSentinel Validation verfügbar" if de else "BCSentinel Validation available"),
            (f"<p>Ihre Validation ist freigeschaltet. Starten Sie jetzt einen neuen Data Health Scan. Der Ergebniszugang gilt anschließend bis {valid_until}.</p>" if de else f"<p>Your Validation is available. Start a new Data Health Scan now. Result access will remain available through {valid_until}.</p>"),
        )
    if event_type in {EVENT_ASSESSMENT_EXPIRING, EVENT_VALIDATION_EXPIRING}:
        label = "Assessment" if event_type == EVENT_ASSESSMENT_EXPIRING else "Validation"
        return (
            (f"BCSentinel {label}: Zugang läuft bald ab" if de else f"BCSentinel {label}: access expires soon"),
            (f"<p>Ihr {label}-Zugang läuft am <strong>{valid_until}</strong> ab. Laden Sie Ihren Report herunter und planen Sie bei Bedarf die nächsten Schritte.</p>" if de else f"<p>Your {label} access expires at <strong>{valid_until}</strong>. Download your report and plan next steps if needed.</p>"),
        )
    if event_type == EVENT_ASSESSMENT_EXPIRED:
        return (
            ("BCSentinel Assessment-Zugang abgelaufen" if de else "BCSentinel Assessment access expired"),
            ("<p>Der Live-Zugriff auf die vollständigen Assessment-Details ist abgelaufen. Der gespeicherte Scan bleibt für Validation und Historie erhalten.</p>" if de else "<p>Live access to full Assessment details has expired. The stored scan remains available for Validation and history.</p>"),
        )
    return ("BCSentinel update", "<p>BCSentinel lifecycle update.</p>")


def _send_html_email(*, target_email: str, subject: str, html_body: str) -> None:
    if not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL:
        raise RuntimeError("SMTP delivery is not configured.")
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = formataddr((settings.SMTP_FROM_NAME, settings.SMTP_FROM_EMAIL))
    message["To"] = target_email
    message.set_content("BCSentinel notification. Please view this message in an HTML-capable email client.")
    message.add_alternative(
        f"<html><body style='font-family:Arial,sans-serif;color:#172033'><div style='max-width:640px;margin:auto'><h2 style='color:#14213D'>BCSentinel</h2>{html_body}<hr><p style='font-size:12px;color:#667085'>Clean Data – Higher Impact</p></div></body></html>",
        subtype="html",
    )
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
        if settings.SMTP_USE_TLS:
            smtp.starttls()
        if settings.SMTP_USERNAME:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD or "")
        smtp.send_message(message)


def process_due_outbox(db, *, limit: int = 25) -> dict[str, int]:
    now = utc_now()
    rows = db.scalars(
        select(LifecycleEmailOutbox)
        .where(
            LifecycleEmailOutbox.status.in_(["queued", "failed"]),
            LifecycleEmailOutbox.scheduled_at_utc <= now,
            LifecycleEmailOutbox.attempts < MAX_ATTEMPTS,
        )
        .order_by(LifecycleEmailOutbox.scheduled_at_utc.asc(), LifecycleEmailOutbox.id.asc())
        .limit(max(1, min(limit, 100)))
    ).all()
    sent = failed = 0
    for row in rows:
        try:
            payload = json.loads(row.payload_json or "{}")
            subject, body = _event_copy(row.event_type, normalize_language(row.language), payload)
            _send_html_email(target_email=row.target_email, subject=subject, html_body=body)
            row.status = "sent"
            row.sent_at_utc = utc_now()
            row.last_error = None
            sent += 1
        except Exception as exc:
            row.status = "failed"
            row.last_error = str(exc)[:1000]
            row.scheduled_at_utc = utc_now() + timedelta(minutes=RETRY_MINUTES)
            failed += 1
        finally:
            row.attempts += 1
            row.updated_at_utc = utc_now()
            db.flush()
    return {"processed": len(rows), "sent": sent, "failed": failed}
