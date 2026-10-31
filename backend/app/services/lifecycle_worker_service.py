from __future__ import annotations

from datetime import timedelta
import json

from sqlalchemy import select, update

from app.lifecycle_models import LifecycleEmailOutbox
from app.services.lifecycle_email_service import (
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

    A worker may terminate after claiming a row but before delivery state is
    persisted. Rows left in `sending` longer than the retry window are safe to
    retry because the provider send did not receive a committed `sent` state.
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


def process_due_outbox_safely(db, *, limit: int = 25) -> dict[str, int]:
    """Claim and deliver due lifecycle email rows without duplicate workers.

    PostgreSQL workers use SELECT .. FOR UPDATE SKIP LOCKED, so one row can be
    processed by only one worker at a time. SQLite used in tests safely ignores
    the locking hint. The claim is marked `sending` before provider I/O and
    stale claims are recoverable on a later cycle.
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
            row.updated_at_utc = utc_now()
            db.flush()

    return {
        "processed": len(rows),
        "sent": sent,
        "failed": failed,
        "recovered": recovered,
    }
