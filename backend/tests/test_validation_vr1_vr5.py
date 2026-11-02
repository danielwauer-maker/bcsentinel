from types import SimpleNamespace

from app.models import TenantScanCredit
from app.schemas.validation_report import ValidationReport
from app.services.validation_report_service import (
    BUSINESS_AREAS,
    _affected_records,
    _business_area_deltas,
    _business_area_label,
    _normalize_category,
)


def test_vr1_validation_uses_canonical_business_areas():
    assert BUSINESS_AREAS == (
        "Finance",
        "Sales",
        "Purchasing",
        "Inventory",
        "CRM",
        "Manufacturing",
        "Service",
        "Jobs",
        "HR",
        "System",
    )
    assert _normalize_category("purchase", "") == "Purchasing"
    assert _normalize_category("customer", "") == "CRM"
    assert _normalize_category(None, "ITEM_STALE") == "Inventory"
    assert _normalize_category(None, "G_L_LEDGER_GAP") == "Finance"
    assert _normalize_category("unknown", "OTHER") == "System"


def test_vr1_validation_localizes_business_area_labels_without_changing_keys():
    assert _business_area_label("Purchasing", "de") == "Einkauf"
    assert _business_area_label("Inventory", "de") == "Lager & Artikel"
    assert _business_area_label("CRM", "de") == "CRM & Stammdaten"
    assert _business_area_label("Purchasing", "en") == "Purchasing"


def _scan(**overrides):
    values = {
        "finance_score": 100,
        "sales_score": 100,
        "purchasing_score": 100,
        "inventory_score": 100,
        "crm_score": 100,
        "manufacturing_score": 100,
        "service_score": 100,
        "jobs_score": 100,
        "hr_score": 100,
        "system_score": 100,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _issue(code, category, affected, impact):
    return SimpleNamespace(
        code=code,
        category=category,
        affected_count=affected,
        estimated_impact_eur=impact,
    )


def test_vr2_business_area_deltas_cover_all_ten_areas_and_signed_changes():
    baseline = _scan(inventory_score=61)
    validation = _scan(inventory_score=78)
    before = {
        "ITEM_A": _issue("ITEM_A", "inventory", 50, 12000),
        "ITEM_B": _issue("ITEM_B", "inventory", 10, 3000),
    }
    after = {
        "ITEM_A": _issue("ITEM_A", "inventory", 20, 5000),
    }

    rows = _business_area_deltas(baseline, validation, before, after, "de")

    assert len(rows) == 10
    inventory = next(row for row in rows if row.name == "Inventory")
    assert inventory.label == "Lager & Artikel"
    assert inventory.baseline_score == 61
    assert inventory.validation_score == 78
    assert inventory.score_delta == 17
    assert inventory.baseline_findings_count == 2
    assert inventory.validation_findings_count == 1
    assert inventory.findings_delta == -1
    assert inventory.baseline_affected_records == 60
    assert inventory.validation_affected_records == 20
    assert inventory.affected_records_delta == -40
    assert inventory.baseline_estimated_impact_eur == 15000
    assert inventory.validation_estimated_impact_eur == 5000
    assert inventory.estimated_impact_delta_eur == -10000


def test_vr3_affected_records_are_derived_consistently_from_finding_projection():
    rows = {
        "A": _issue("A", "finance", 25, 1000),
        "B": _issue("B", "sales", 15, 500),
        "C": _issue("C", "system", -5, 0),
    }
    assert _affected_records(rows) == 40


def test_vr3_contract_preserves_signed_business_impact_delta():
    fields = ValidationReport.model_fields
    assert "baseline_affected_records" in fields
    assert "validation_affected_records" in fields
    assert "affected_records_delta" in fields
    assert "business_impact_delta_eur" in fields
    assert fields["business_impact_delta_eur"].default == 0.0


def test_vr4_validation_credit_can_persist_exact_baseline_scan():
    assert "baseline_scan_id" in TenantScanCredit.__table__.columns
    assert TenantScanCredit.__table__.columns["baseline_scan_id"].nullable is True


def test_vr4_report_exposes_baseline_reference_provenance():
    fields = ValidationReport.model_fields
    assert "baseline_reference_source" in fields
    assert fields["baseline_reference_source"].default == "legacy_prior_assessment"
