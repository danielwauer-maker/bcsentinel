from __future__ import annotations

from datetime import timedelta
import html
import json

from sqlalchemy import select, update

from app.lifecycle_models import LifecycleEmailOutbox
from app.services.lifecycle_email_service import (
    EVENT_SCAN_STARTED,
    EVENT_VALIDATION_AVAILABLE,
    MAX_ATTEMPTS,
    RETRY_MINUTES,
    _event_copy,
    _send_html_email,
    normalize_language,
    utc_now,
)

SENDING_STALE_MINUTES = 15


def recover_stale_sending(db) -> int:
    """Return abandoned delivery claims to the retry queue.

    Delivery is intentionally at-least-once: if a process terminates after the
    SMTP provider accepted a message but before the local `sent` state commits,
    a retry can occur. Dedupe keys prevent duplicate queue rows, while the stale
    claim recovery prevents permanent loss after worker termination.
    """
    now = utc_now()
    result = db.execute(
        update(LifecycleEmailOutbox)
        .where(
            LifecycleEmailOutbox.status == "sending",
            LifecycleEmailOutbox.updated_at_utc <= now - timedelta(minutes=SENDING_STALE_MINUTES),
            LifecycleEmailOutbox.attempts < MAX_ATTEMPTS,
        )
        .values(
            status="failed",
            scheduled_at_utc=now,
            last_error="Recovered abandoned delivery claim.",
            updated_at_utc=now,
        )
    )
    db.flush()
    return int(result.rowcount or 0)


def _worker_event_copy(event_type: str, language: str, payload: dict) -> tuple[str, str]:
    if event_type == EVENT_SCAN_STARTED:
        scan_id = html.escape(str(payload.get("scan_id") or ""))
        if language == "de":
            return (
                "BCSentinel Scan gestartet",
                f"<p>Ihr Data Health Scan <strong>{scan_id}</strong> wurde gestartet. Sie erhalten eine weitere Nachricht, sobald das Ergebnis verfügbar ist.</p>",
            )
        return (
            "BCSentinel scan started",
            f"<p>Your Data Health Scan <strong>{scan_id}</strong> has started. You will receive another message when the result is available.</p>",
        )
    if event_type == EVENT_VALIDATION_AVAILABLE and not payload.get("valid_until_utc"):
        baseline_scan_id = html.escape(str(payload.get("baseline_scan_id") or ""))
        if language == "de":
            return (
                "BCSentinel Validation verfügbar",
                f"<p>Ihre Validation ist freigeschaltet. Starten Sie jetzt einen neuen Data Health Scan. Das 7-Tage-Fenster für vollständige Validation-Ergebnisse beginnt mit diesem neuen Scan.</p><p>Baseline: <strong>{baseline_scan_id}</strong></p>",
            )
        return (
            "BCSentinel Validation available",
            f"<p>Your Validation is available. Start a new Data Health Scan now. The 7-day full Validation result window begins with that new scan.</p><p>Baseline: <strong>{baseline_scan_id}</strong></p>",
        )
    return _event_copy(event_type, language, payload)


def process_due_outbox_safely(db, *, limit: int = 25) -> dict[str, int]:
    """Claim and deliver due lifecycle email rows across multiple workers.

    PostgreSQL workers use SELECT .. FOR UPDATE SKIP LOCKED, so a due row is
    claimed by only one concurrent worker transaction. SQLite used in tests
    safely ignores the locking hint. Stale claims are recoverable later.
    """
    recovered = recover_stale_sending(db)
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
        .with_for_update(skip_locked=True)
    ).all()

    sent = failed = 0
    for row in rows:
        row.status = "sending"
        row.attempts += 1
        row.updated_at_utc = utc_now()
        db.flush()
        try:
            payload = json.loads(row.payload_json or "{}")
            subject, body = _worker_event_copy(row.event_type, normalize_language(row.language), payload)
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
            row.updated_at_utc = utc_now()
            db.flush()

    return {
        "processed": len(rows),
        "sent": sent,
        "failed": failed,
        "recovered": recovered,
    }
