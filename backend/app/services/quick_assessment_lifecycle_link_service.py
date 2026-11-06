from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import quote

from jose import jwt

from app.core.settings import resolve_public_base_url, settings

QUICK_REPORT_SHARE_ALGORITHM = "HS256"
QUICK_REPORT_SHARE_TOKEN_TYPE = "quick_assessment_report_share"


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def quick_assessment_lifecycle_report_link(
    *,
    tenant_id: str,
    scan_id: str,
    valid_until_utc: datetime,
) -> str | None:
    """Create a revocable Quick report link that never outlives Quick access."""
    base_url = resolve_public_base_url()
    if not base_url:
        return None
    payload = {
        "type": QUICK_REPORT_SHARE_TOKEN_TYPE,
        "tenant_id": tenant_id,
        "scan_id": scan_id,
        "report_type": "html",
        "exp": _as_utc(valid_until_utc),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=QUICK_REPORT_SHARE_ALGORITHM)
    return f"{base_url}/reports/quick-assessment/{quote(scan_id)}/html/shared?token={quote(token)}"
