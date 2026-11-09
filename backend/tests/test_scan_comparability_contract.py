from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from app.services.scan_comparability_service import (
    CheckEvidence, CheckStatus, Reason, ScanEvidence, catalog_fingerprint,
    compare_scans, finding_comparison_identity,
)


COMPANY = "11111111-2222-3333-4444-555555555555"
RECORD = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
NOW = datetime(2026, 11, 9, tzinfo=timezone.utc)


def evidence(**overrides):
    value = ScanEvidence(
        tenant_id="tenant-a", company_id=COMPANY, environment="sandbox", currency="EUR",
        methodology_version="method-v1", catalog_version="catalog-v1", catalog_fingerprint="a" * 64,
        modules=("sales", "finance"), expected_checks=("A", "B"),
        checks=(CheckEvidence("A", CheckStatus.PASS), CheckEvidence("B", CheckStatus.FINDINGS, True)),
        completed_at=NOW, result_persisted_at=NOW, scan_status="completed", source_verified=True,
    )
    return replace(value, **overrides)


def test_catalog_fingerprint_is_order_independent_and_versioned():
    a = catalog_fingerprint("catalog-v1", "method-v1", (("A", "SALES"), ("B", "FINANCE")))
    b = catalog_fingerprint("catalog-v1", "method-v1", (("b", "finance"), ("a", "sales")))
    assert a == b
    assert a != catalog_fingerprint("catalog-v1", "method-v2", (("A", "SALES"), ("B", "FINANCE")))
    with pytest.raises(ValueError):
        catalog_fingerprint("v1", "v1", (("A", "SALES"), ("a", "SALES")))


def test_record_identity_is_stable_and_scoped_without_finding_row_id():
    args = dict(tenant_id="tenant-a", company_id=COMPANY, check_code="CHK", methodology_version="v1",
                module_code="SALES", finding_type="record", criterion="missing-email", record_system_id=RECORD)
    identity = finding_comparison_identity(**args)
    assert identity and identity == finding_comparison_identity(**args)
    for change in ({"tenant_id": "tenant-b"}, {"company_id": "99999999-2222-3333-4444-555555555555"},
                   {"record_system_id": "bbbbbbbb-bbbb-cccc-dddd-eeeeeeeeeeee"},
                   {"methodology_version": "v2"}, {"criterion": "missing-phone"}, {"finding_type": "group"}):
        assert identity != finding_comparison_identity(**(args | change))
    assert finding_comparison_identity(**(args | {"record_system_id": None})) is None
    assert finding_comparison_identity(**(args | {"record_system_id": "00000000-0000-0000-0000-000000000000"})) is None


def test_complete_check_comparison_never_invents_score_or_impact_compatibility():
    current = evidence(completed_at=NOW + timedelta(days=1), modules=("FINANCE", "SALES"), expected_checks=("B", "A"))
    result = compare_scans(evidence(), current)
    assert result.comparable and result.comparable_checks == ("A", "B")
    assert not result.health_score_comparable and not result.impact_comparable


@pytest.mark.parametrize(("field", "value", "reason"), [
    ("tenant_id", "tenant-b", Reason.TENANT_MISMATCH),
    ("company_id", "99999999-2222-3333-4444-555555555555", Reason.COMPANY_MISMATCH),
    ("environment", "production", Reason.ENVIRONMENT_MISMATCH),
    ("currency", "USD", Reason.CURRENCY_MISMATCH),
    ("methodology_version", "method-v2", Reason.METHODOLOGY_MISMATCH),
    ("catalog_fingerprint", "b" * 64, Reason.CATALOG_MISMATCH),
    ("modules", ("SALES",), Reason.SCOPE_MISMATCH),
    ("source_verified", False, Reason.MISSING_PROVENANCE),
    ("completed_at", NOW - timedelta(days=1), Reason.INVALID_SCAN_ORDER),
    ("scan_status", "failed", Reason.INCOMPLETE_CHECK_COVERAGE),
    ("result_persisted_at", None, Reason.INCOMPLETE_CHECK_COVERAGE),
])
def test_mismatches_are_explicit_and_fail_closed(field, value, reason):
    current = evidence(completed_at=NOW + timedelta(days=1))
    result = compare_scans(evidence(), replace(current, **{field: value}))
    assert not result.comparable and reason in result.reasons
    assert not result.health_score_comparable and not result.impact_comparable


@pytest.mark.parametrize("status", [CheckStatus.FAILED, CheckStatus.SKIPPED, CheckStatus.NOT_EXECUTED])
def test_partial_check_execution_never_proves_a_complete_comparison(status):
    current = evidence(completed_at=NOW + timedelta(days=1), checks=(CheckEvidence("A", CheckStatus.PASS), CheckEvidence("B", status)))
    result = compare_scans(evidence(), current)
    assert not result.comparable and Reason.INCOMPLETE_CHECK_COVERAGE in result.reasons
    assert result.comparable_checks == ("A",)


def test_missing_or_ambiguous_evidence_never_becomes_comparable():
    assert compare_scans(None, evidence()).reasons == (Reason.MISSING_PROVENANCE,)
    duplicate = evidence(completed_at=NOW + timedelta(days=1), checks=(CheckEvidence("A", CheckStatus.PASS), CheckEvidence("a", CheckStatus.PASS)))
    assert Reason.MISSING_PROVENANCE in compare_scans(evidence(), duplicate).reasons
    unstable = evidence(completed_at=NOW + timedelta(days=1), checks=(CheckEvidence("A", CheckStatus.PASS), CheckEvidence("B", CheckStatus.FINDINGS)))
    assert Reason.UNSTABLE_FINDING_IDENTITY in compare_scans(evidence(), unstable).reasons
    failed = evidence(completed_at=NOW + timedelta(days=1), scan_status="failed")
    assert compare_scans(evidence(), failed).comparable_checks == ()
