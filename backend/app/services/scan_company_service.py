"""Canonical BC company and currency identity for scan-time report snapshots."""
from __future__ import annotations

from uuid import UUID


def canonical_company_id(raw: str) -> str:
    try:
        parsed = UUID(str(raw or "").strip().strip("{}"))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError("Invalid BC Company GUID.") from exc
    if parsed.int == 0:
        raise ValueError("BC Company GUID cannot be null.")
    return str(parsed)


def canonical_lcy_code(raw: str) -> str:
    code = str(raw or "").strip().upper()
    if len(code) != 3 or not code.isascii() or not code.isalpha():
        raise ValueError("Local currency code must be three ASCII letters.")
    return code
