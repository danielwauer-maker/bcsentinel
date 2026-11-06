"""Protect scan-time BC company and LCY identities during sync/replay.

These tests do not consume a scan credit or require DEV services.
"""
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.routers.scans import ScanSyncPayload, _resolve_verified_scan_binding

COMPANY = "11111111-2222-3333-4444-555555555555"
OTHER = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def payload(company_id=None, lcy_code=None):
    return ScanSyncPayload(
        tenant_id="tenant-a", scan_id="scan-a", scan_type="deep",
        generated_at_utc=datetime.now(timezone.utc), data_score=80,
        checks_count=202, issues_count=95,
        bc_company_id=company_id, lcy_code=lcy_code,
    )


def test_company_and_lcy_are_canonicalized():
    tenant = SimpleNamespace(bc_company_id="{" + COMPANY.upper() + "}")
    binding = _resolve_verified_scan_binding(payload(COMPANY.upper(), "eur"), tenant, None)
    assert binding == (COMPANY, "EUR")


def test_missing_identity_is_not_inferred_from_tenant():
    tenant = SimpleNamespace(bc_company_id=COMPANY)
    assert _resolve_verified_scan_binding(payload(), tenant, None) == (None, None)


@pytest.mark.parametrize("company,code", [
    (COMPANY, None), (None, "EUR"), ("not-a-guid", "EUR"),
    (COMPANY, "EURO"), (COMPANY, "12A"),
])
def test_incomplete_or_invalid_company_evidence_rejected(company, code):
    tenant = SimpleNamespace(bc_company_id=COMPANY)
    with pytest.raises(HTTPException) as error:
        _resolve_verified_scan_binding(payload(company, code), tenant, None)
    assert error.value.status_code == 422


def test_other_registered_company_is_not_accepted():
    tenant = SimpleNamespace(bc_company_id=COMPANY)
    with pytest.raises(HTTPException) as error:
        _resolve_verified_scan_binding(payload(OTHER, "EUR"), tenant, None)
    assert error.value.status_code == 409


def test_existing_scan_cannot_be_rebound_to_other_company_or_currency():
    tenant = SimpleNamespace(bc_company_id="")
    stored = SimpleNamespace(bc_company_id=COMPANY, lcy_code="EUR")
    for changed in [payload(OTHER, "EUR"), payload(COMPANY, "USD")]:
        with pytest.raises(HTTPException) as error:
            _resolve_verified_scan_binding(changed, tenant, stored)
        assert error.value.status_code == 409


def test_replay_without_fields_preserves_existing_binding():
    tenant = SimpleNamespace(bc_company_id=COMPANY)
    stored = SimpleNamespace(bc_company_id=COMPANY, lcy_code="EUR")
    assert _resolve_verified_scan_binding(payload(), tenant, stored) == (None, None)
