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
        tenant_id="tenant-a", scan_id="scan-before", company_id=COMPANY, environment="sandbox", currency="EUR",
        methodology_version="method-v1", catalog_version="catalog-v1", catalog_fingerprint="a" * 64,
        modules=("sales", "finance"), expected_checks=("A", "B"),
        checks=(CheckEvidence("A", CheckStatus.PASS), CheckEvidence("B", CheckStatus.FINDINGS, True)),
        completed_at=NOW, result_persisted_at=NOW, scan_status="completed", source_verified=True,
    )
    if "completed_at" in overrides and "scan_id" not in overrides:
        overrides["scan_id"] = "scan-after"
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
    ("scan_id", "scan-before", Reason.SAME_SCAN),
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


def test_scope_mismatch_does_not_assume_check_scope_independence():
    current = evidence(completed_at=NOW + timedelta(days=1), modules=("SALES",))
    result = compare_scans(evidence(), current)
    assert Reason.SCOPE_MISMATCH in result.reasons
    assert result.comparable_checks == ()


def test_missing_or_ambiguous_evidence_never_becomes_comparable():
    assert compare_scans(None, evidence()).reasons == (Reason.MISSING_PROVENANCE,)
    assert compare_scans(evidence(), evidence(environment=None)).reasons == (Reason.MISSING_PROVENANCE,)
    duplicate = evidence(completed_at=NOW + timedelta(days=1), checks=(CheckEvidence("A", CheckStatus.PASS), CheckEvidence("a", CheckStatus.PASS)))
    assert Reason.MISSING_PROVENANCE in compare_scans(evidence(), duplicate).reasons
    unstable = evidence(completed_at=NOW + timedelta(days=1), checks=(CheckEvidence("A", CheckStatus.PASS), CheckEvidence("B", CheckStatus.FINDINGS)))
    assert Reason.UNSTABLE_FINDING_IDENTITY in compare_scans(evidence(), unstable).reasons
    failed = evidence(completed_at=NOW + timedelta(days=1), scan_status="failed")
    assert compare_scans(evidence(), failed).comparable_checks == ()


def test_verified_record_finding_transitions_are_set_based_and_order_independent():
    from app.services.scan_comparability_service import compare_verified_finding_sets

    a, b, c = ("a" * 64, "b" * 64, "c" * 64)
    result = compare_verified_finding_sets(
        previous_identities=(b, a),
        current_identities=(c, b),
        previous_check=CheckEvidence("CHK", CheckStatus.FINDINGS, True),
        current_check=CheckEvidence("CHK", CheckStatus.FINDINGS, True),
    )
    assert result.resolved == (a,)
    assert result.persistent == (b,)
    assert result.new == (c,)


def test_verified_record_finding_transitions_support_empty_healthy_scans():
    from app.services.scan_comparability_service import compare_verified_finding_sets

    a = "a" * 64
    result = compare_verified_finding_sets(
        previous_identities=(a,),
        current_identities=(),
        previous_check=CheckEvidence("CHK", CheckStatus.FINDINGS, True),
        current_check=CheckEvidence("CHK", CheckStatus.PASS),
    )
    assert result.resolved == (a,) and not result.persistent and not result.new


@pytest.mark.parametrize(("before", "after", "old", "new"), [
    (("a" * 64,), (), CheckEvidence("CHK", CheckStatus.FINDINGS), CheckEvidence("CHK", CheckStatus.PASS)),
    (("a" * 64,), (), CheckEvidence("CHK", CheckStatus.FAILED, True), CheckEvidence("CHK", CheckStatus.PASS)),
    (("a" * 64,), (), CheckEvidence("CHK", CheckStatus.FINDINGS, True), CheckEvidence("OTHER", CheckStatus.PASS)),
    (("a" * 64, "a" * 64), (), CheckEvidence("CHK", CheckStatus.FINDINGS, True), CheckEvidence("CHK", CheckStatus.PASS)),
    (("legacy:CHK",), (), CheckEvidence("CHK", CheckStatus.FINDINGS, True), CheckEvidence("CHK", CheckStatus.PASS)),
    ((), (), CheckEvidence("CHK", CheckStatus.FINDINGS, True), CheckEvidence("CHK", CheckStatus.PASS)),
    (("a" * 64,), ("b" * 64,), CheckEvidence("CHK", CheckStatus.FINDINGS, True), CheckEvidence("CHK", CheckStatus.PASS)),
])
def test_unverified_or_inconsistent_finding_transition_inputs_fail_closed(before, after, old, new):
    from app.services.scan_comparability_service import compare_verified_finding_sets

    with pytest.raises(ValueError):
        compare_verified_finding_sets(
            previous_identities=before, current_identities=after,
            previous_check=old, current_check=new,
        )


def test_scan_bound_finding_transitions_require_verified_full_scan_evidence():
    from app.services.scan_comparability_service import compare_verified_scan_finding_sets

    current = evidence(
        scan_id="scan-after", completed_at=NOW + timedelta(days=1),
        checks=(CheckEvidence("A", CheckStatus.PASS), CheckEvidence("B", CheckStatus.FINDINGS, True)),
    )
    args = {
        "previous": evidence(),
        "current": current,
        "check_code": "B",
        "previous_identities": ("a" * 64, "b" * 64),
        "current_identities": ("b" * 64, "c" * 64),
    }
    changed = compare_verified_scan_finding_sets(**args)
    assert changed.resolved == ("a" * 64,)
    assert changed.persistent == ("b" * 64,)
    assert changed.new == ("c" * 64,)
    with pytest.raises(ValueError):
        compare_verified_scan_finding_sets(**(args | {"current": replace(current, source_verified=False)}))
    with pytest.raises(ValueError):
        compare_verified_scan_finding_sets(**(args | {"current": replace(current, company_id="99999999-2222-3333-4444-555555555555")}))
    with pytest.raises(ValueError):
        compare_verified_scan_finding_sets(**(args | {"current": replace(current, modules=("SALES",))}))
    with pytest.raises(ValueError):
        compare_verified_scan_finding_sets(**(args | {"current": replace(current, checks=(CheckEvidence("A", CheckStatus.PASS), CheckEvidence("B", CheckStatus.FINDINGS)))}))
    with pytest.raises(ValueError):
        compare_verified_scan_finding_sets(**(args | {"check_code": "UNKNOWN"}))
