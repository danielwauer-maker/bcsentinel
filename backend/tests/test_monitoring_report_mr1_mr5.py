from datetime import datetime, timezone
from types import SimpleNamespace

from app.schemas.monitoring_report import MonitoringReport
from app.services.monitoring_report_service import (
    BUSINESS_AREAS,
    _area_trend,
    _business_area_trends,
    _finding_lifecycle,
    _trend_points,
)


def _scan(scan_id: str, day: int, score: int, **overrides):
    values = {
        "scan_id": scan_id,
        "id": day,
        "generated_at_utc": datetime(2026, 1, day, tzinfo=timezone.utc),
        "data_score": score,
        "finance_score": 60,
        "sales_score": 65,
        "purchasing_score": 70,
        "inventory_score": 68,
        "crm_score": 71,
        "manufacturing_score": 78,
        "service_score": 73,
        "jobs_score": 69,
        "hr_score": 76,
        "system_score": 80,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _issue(code: str, category: str, severity: str, affected: int, impact: float, title: str | None = None):
    return SimpleNamespace(
        code=code,
        category=category,
        severity=severity,
        affected_count=affected,
        estimated_impact_eur=impact,
        title=title or code,
    )


def test_mr1_has_dedicated_monitoring_contract():
    fields = MonitoringReport.model_fields
    assert fields["contract_version"].default == "monitoring-report-v1"
    assert fields["report_variant"].default == "monitoring"
    assert "trend_points" in fields
    assert "business_areas" in fields
    assert "finding_lifecycle" in fields
    assert "coverage" in fields


def test_mr2_trend_points_preserve_historical_scan_order_and_metrics():
    scans = [_scan("S1", 1, 68), _scan("S2", 8, 72), _scan("S3", 15, 79)]
    issues = {
        "S1": {"A": _issue("A", "finance", "critical", 20, 10000)},
        "S2": {"A": _issue("A", "finance", "high", 10, 6000)},
        "S3": {},
    }
    points = _trend_points(scans, issues)
    assert [point.scan_id for point in points] == ["S1", "S2", "S3"]
    assert [point.data_health_score for point in points] == [68, 72, 79]
    assert points[0].affected_records == 20
    assert points[1].modeled_business_impact_eur == 6000
    assert points[2].findings_count == 0


def test_mr3_finding_lifecycle_detects_resolved_reopened_new_improving_and_regressing():
    scans = [_scan("S1", 1, 60), _scan("S2", 8, 65), _scan("S3", 15, 70)]
    issues = {
        "S1": {
            "RES": _issue("RES", "finance", "high", 10, 5000),
            "REO": _issue("REO", "sales", "medium", 5, 1000),
            "IMP": _issue("IMP", "inventory", "critical", 20, 10000),
            "REG": _issue("REG", "service", "medium", 5, 1000),
        },
        "S2": {
            "IMP": _issue("IMP", "inventory", "high", 10, 6000),
            "REG": _issue("REG", "service", "medium", 5, 1000),
        },
        "S3": {
            "REO": _issue("REO", "sales", "medium", 5, 1000),
            "IMP": _issue("IMP", "inventory", "medium", 5, 3000),
            "REG": _issue("REG", "service", "high", 7, 1500),
            "NEW": _issue("NEW", "crm", "medium", 4, 800),
        },
    }
    rows = {row.code: row for row in _finding_lifecycle(scans, issues, "de")}
    assert rows["RES"].status == "resolved"
    assert rows["REO"].status == "reopened"
    assert rows["NEW"].status == "new"
    assert rows["IMP"].status == "improving"
    assert rows["REG"].status == "regressing"
    assert rows["NEW"].category_label == "CRM & Stammdaten"


def test_mr4_business_area_trends_cover_all_ten_canonical_areas():
    scans = [
        _scan("S1", 1, 68, inventory_score=60),
        _scan("S2", 8, 70, inventory_score=70),
        _scan("S3", 15, 74, inventory_score=80),
    ]
    issues = {
        "S1": {"A": _issue("A", "inventory", "high", 10, 10000)},
        "S2": {"A": _issue("A", "inventory", "high", 8, 7000)},
        "S3": {"A": _issue("A", "inventory", "medium", 5, 4000)},
    }
    rows = _business_area_trends(scans, issues, "de")
    assert len(rows) == len(BUSINESS_AREAS) == 10
    inventory = next(row for row in rows if row.name == "Inventory")
    assert inventory.label == "Lager & Artikel"
    assert inventory.baseline_score == 60
    assert inventory.previous_score == 70
    assert inventory.current_score == 80
    assert inventory.score_delta_previous == 10
    assert inventory.impact_delta_previous_eur == -3000
    assert inventory.trend == "improving"


def test_mr4_area_trend_does_not_call_mixed_signals_improvement():
    assert _area_trend(5, -1000) == "improving"
    assert _area_trend(-5, 1000) == "deteriorating"
    assert _area_trend(5, 1000) == "stable"
    assert _area_trend(-5, -1000) == "stable"
