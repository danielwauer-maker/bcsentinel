"""Regression for the read-only DEV acceptance script (no network calls)."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_script():
    path = Path(__file__).resolve().parents[2] / "scripts" / "check_dev_bc_acceptance.py"
    spec = spec_from_file_location("bcsentinel_acceptance_preflight", path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ready_response():
    return {
        "preflight_only": True,
        "scan_id": "test-original-free",
        "original_free_scan": True,
        "company_bound": True,
        "company_id": "11111111-2222-3333-4444-555555555555",
        "eur_currency_verified": True,
        "premium_active": True,
        "scope_state": "auto",
        "confirmed_scope_version": None,
        "missing_prerequisites": ["confirmed_scope_missing"],
    }


def test_ready_original_free_scan_needs_only_manual_confirmation():
    ready, blockers = _load_script().evaluate(_ready_response(), None)
    assert ready is True
    assert blockers == []


def test_no_unverified_baseline_or_legacy_preflight_is_accepted():
    evaluate = _load_script().evaluate
    for value in (False, None):
        info = _ready_response()
        info["original_free_scan"] = value
        assert evaluate(info, None)[0] is False


def test_backend_missing_evidence_cannot_be_ignored():
    evaluate = _load_script().evaluate
    info = _ready_response()
    info["missing_prerequisites"].append("original_completed_free_scan_missing")
    assert evaluate(info, None)[0] is False
    info["missing_prerequisites"] = "not-a-list"
    assert evaluate(info, None)[0] is False


def test_expected_company_guid_is_verified_exactly():
    evaluate = _load_script().evaluate
    assert evaluate(_ready_response(), "11111111-2222-3333-4444-555555555555") == (True, [])
    assert evaluate(_ready_response(), "{11111111-2222-3333-4444-555555555555}") == (True, [])
    ready, blockers = evaluate(_ready_response(), "aaaaaaaa-2222-3333-4444-555555555555")
    assert not ready
    assert any("GUID" in blocker for blocker in blockers)


def test_missing_or_invalid_company_guid_fails_closed_even_if_bound():
    evaluate = _load_script().evaluate
    for raw in (None, "", "not-a-guid", "00000000-0000-0000-0000-000000000000"):
        info = _ready_response()
        info["company_id"] = raw
        assert evaluate(info, None)[0] is False


def test_malformed_expected_company_guid_is_rejected():
    ready, blockers = _load_script().evaluate(_ready_response(), "not-a-guid")
    assert not ready
    assert any("malformed" in blocker for blocker in blockers)
