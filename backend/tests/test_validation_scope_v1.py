from types import SimpleNamespace

from app.assessment_scope_models import ValidationScopeBinding
from app.schemas.validation_report import ValidationFindingDelta
from app.services.validation_scope_report_service import _filter_findings, _validation_score


def _finding(code: str, category: str) -> ValidationFindingDelta:
    return ValidationFindingDelta(
        code=code,
        title=code,
        category=category,
        category_label=category,
        severity_before="high",
        severity_after="medium",
        affected_before=10,
        affected_after=5,
        impact_before_eur=1000,
        impact_after_eur=500,
        status="improved",
    )


def test_validation_scope_binding_is_unique_per_validation_scan():
    constraint_names = {constraint.name for constraint in ValidationScopeBinding.__table__.constraints}
    assert "uq_validation_scope_validation_scan" in constraint_names


def test_validation_scope_filters_findings_to_confirmed_modules():
    rows = [
        _finding("SALES_A", "Sales"),
        _finding("HR_A", "HR"),
        _finding("ITEM_A", "Inventory"),
    ]
    filtered = _filter_findings(rows, {"sales", "inventory", "system"})
    assert [row.code for row in filtered] == ["SALES_A", "ITEM_A"]


def test_validation_score_reuses_same_confirmed_module_set():
    scan = SimpleNamespace(
        sales_score=80,
        inventory_score=90,
        system_score=100,
        hr_score=20,
    )
    score = _validation_score(scan, {"sales", "inventory", "system"}, 0)
    assert score == 90
