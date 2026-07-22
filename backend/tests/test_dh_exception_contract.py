from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.routers.scans import ScanSyncPayload


def _payload(**overrides):
    values = {
        "tenant_id": "tenant-exception-contract",
        "scan_id": "scan-exception-contract",
        "scan_type": "deep",
        "generated_at_utc": datetime.now(timezone.utc),
        "data_score": 90,
        "checks_count": 10,
        "issues_count": 1,
    }
    values.update(overrides)
    return values


def test_legacy_scan_payload_defaults_applied_exception_count_to_zero():
    payload = ScanSyncPayload(**_payload())

    assert payload.applied_exception_count == 0


@pytest.mark.parametrize("count", [1, 4])
def test_scan_payload_accepts_non_negative_applied_exception_count(count):
    payload = ScanSyncPayload(**_payload(applied_exception_count=count))

    assert payload.applied_exception_count == count


def test_scan_payload_rejects_negative_applied_exception_count():
    with pytest.raises(ValidationError):
        ScanSyncPayload(**_payload(applied_exception_count=-1))
