from __future__ import annotations

import json
from pathlib import Path

from app.core.product_model import Entitlement, OFFER_ENTITLEMENTS, CommercialOffer


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPOSITORY_ROOT / "quality" / "s04b-package-a-contract.json"


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_contract_uses_only_canonical_entitlement_ids() -> None:
    contract = _contract()
    canonical_ids = {item.value for item in Entitlement}

    for tier in contract["tiers"].values():
        assert set(tier["required_capabilities"]).issubset(canonical_ids)


def test_assessment_contract_matches_canonical_assessment_entitlements() -> None:
    contract = _contract()
    required = set(contract["tiers"]["assessment"]["required_capabilities"])
    canonical = {item.value for item in OFFER_ENTITLEMENTS[CommercialOffer.ASSESSMENT]}

    assert required == canonical


def test_monitoring_contract_matches_package_a_subset_of_monitoring_entitlements() -> None:
    contract = _contract()
    required = set(contract["tiers"]["monitoring"]["required_capabilities"])
    canonical = {item.value for item in OFFER_ENTITLEMENTS[CommercialOffer.MONITORING]}

    assert required.issubset(canonical)
    assert {
        Entitlement.MONITORING_SCHEDULE.value,
        Entitlement.MONITORING_HISTORY.value,
        Entitlement.MONITORING_ALERTS.value,
    }.issubset(required)


def test_free_contract_does_not_claim_paid_detail_entitlements() -> None:
    contract = _contract()
    free_required = set(contract["tiers"]["free"]["required_capabilities"])

    assert Entitlement.FINDINGS_SUMMARY.value in free_required
    assert Entitlement.FINDINGS_FULL.value not in free_required
    assert Entitlement.FINDINGS_RECORDS.value not in free_required
    assert Entitlement.ACTIONS_MANAGE.value not in free_required
    assert Entitlement.FINANCIAL_IMPACT_FULL.value not in free_required
    assert Entitlement.REPORT_EXECUTIVE.value not in free_required
    assert Entitlement.MONITORING_HISTORY.value not in free_required


def test_free_contract_explicitly_forbids_sensitive_detail() -> None:
    contract = _contract()
    free = contract["tiers"]["free"]

    overview_forbidden = set(free["overview"]["forbidden"])
    findings_forbidden = set(free["findings"]["forbidden"])
    actions_forbidden = set(free["actions"]["forbidden"])

    assert {"finding_title", "record_identifiers", "root_cause", "recommendation"}.issubset(
        overview_forbidden
    )
    assert {"finding_title", "records", "root_cause", "recommendation"}.issubset(
        findings_forbidden
    )
    assert {"action_title", "remediation_steps", "owner", "record_links"}.issubset(
        actions_forbidden
    )


def test_frontend_is_not_declared_as_authorization_boundary() -> None:
    contract = _contract()

    assert contract["frontend_is_authorization_boundary"] is False
    assert contract["implementation_boundaries"]["production_plan_switch"] == "forbidden"
    assert contract["implementation_boundaries"]["local_storage_entitlement_authority"] == "forbidden"
    assert contract["implementation_boundaries"]["free_paid_data_in_response"] == "forbidden"
