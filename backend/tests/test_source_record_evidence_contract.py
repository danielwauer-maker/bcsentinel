"""Fail-closed tests for the future BC record-identity evidence envelope.

No endpoint or DB persistence is enabled by this schema-level test suite.
"""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.services.source_record_evidence_contract import (
    SourceRecordEvidenceV1, canonical_record_evidence,
    validate_record_evidence_contract,
)


COMPANY = "11111111-2222-3333-4444-555555555555"
NOW = datetime(2026, 11, 10, 10, 0, tzinfo=timezone.utc)
A = "aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa"
B = "bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb"


def source_payload(*, members=(A, B)):
    return {
        "schema_version": "bc-record-evidence-v1",
        "tenant_id": "tenant-1",
        "scan_id": "scan-1",
        "company_id": COMPANY,
        "check_code": "CUSTOMERS_DUPLICATE_VAT",
        "observed_at_utc": NOW.isoformat(),
        "completed": True,
        "affected_records_count": len(members),
        "records": [{"table_id": 18, "record_system_id": member} for member in members],
    }


def verify(payload=None, *, status="FINDINGS", groups=1, affected=2):
    envelope = SourceRecordEvidenceV1.model_validate(payload or source_payload())
    return validate_record_evidence_contract(
        envelope, tenant_id="tenant-1", scan_id="scan-1", company_id=COMPANY,
        check_status=status, group_finding_count=groups, affected_records_count=affected,
    )


def test_canonical_identity_contract_is_order_independent_and_reproducible():
    one = source_payload()
    two = source_payload(members=(B.upper(), A.upper()))
    canonical, digest = verify(one)
    canonical2, digest2 = verify(two)
    assert canonical == canonical2 and digest == digest2
    assert hashlib.sha256(canonical.encode()).hexdigest() == digest
    assert json.loads(canonical)["records"] == [
        {"record_system_id": A, "table_id": 18},
        {"record_system_id": B, "table_id": 18},
    ]
    assert canonical_record_evidence(SourceRecordEvidenceV1.model_validate(one)) == (canonical, digest)


@pytest.mark.parametrize("change", [
    {"schema_version": "bc-record-evidence-v0"},
    {"company_id": "00000000-0000-0000-0000-000000000000"},
    {"completed": False},
    {"check_code": "VENDORS_DUPLICATE_VAT"},
    {"observed_at_utc": (NOW + timedelta(hours=1)).replace(tzinfo=timezone(timedelta(hours=1))).isoformat()},
    {"records": [{"table_id": 23, "record_system_id": A}, {"table_id": 23, "record_system_id": B}]},
    {"records": [{"table_id": 18, "record_system_id": A}, {"table_id": 18, "record_system_id": A}]},
    {"records": [{"table_id": 18, "record_system_id": "00000000-0000-0000-0000-000000000000"},
                 {"table_id": 18, "record_system_id": B}]},
    {"affected_records_count": 1},
    {"affected_records_count": 3},
])
def test_invalid_or_incomplete_identity_payload_is_rejected(change):
    payload = source_payload() | change
    with pytest.raises(ValidationError):
        SourceRecordEvidenceV1.model_validate(payload)


@pytest.mark.parametrize("binding", [
    {"tenant_id": "other"},
    {"scan_id": "other"},
    {"company_id": "22222222-2222-4222-8222-222222222222"},
    {"check_status": "STARTED"},
    {"check_status": "SKIPPED"},
    {"check_status": "PASS"},
    {"group_finding_count": 0},
    {"affected_records_count": 3},
])
def test_tampered_scope_or_unfinished_group_cannot_attest_record_evidence(binding):
    args = dict(
        tenant_id="tenant-1", scan_id="scan-1", company_id=COMPANY,
        check_status="FINDINGS", group_finding_count=1, affected_records_count=2,
    ) | binding
    envelope = SourceRecordEvidenceV1.model_validate(source_payload())
    with pytest.raises(ValueError):
        validate_record_evidence_contract(envelope, **args)


def test_empty_pass_is_allowed_without_inventing_records():
    payload = source_payload(members=())
    canonical, digest = verify(payload, status="PASS", groups=0, affected=0)
    assert json.loads(canonical)["records"] == []
    assert len(digest) == 64


def test_unknown_fields_and_more_than_max_members_fail_closed():
    with pytest.raises(ValidationError):
        SourceRecordEvidenceV1.model_validate(source_payload() | {"record_email": "secret@example.invalid"})
    payload = source_payload(members=(A,) * 2001)
    with pytest.raises(ValidationError):
        SourceRecordEvidenceV1.model_validate(payload)
