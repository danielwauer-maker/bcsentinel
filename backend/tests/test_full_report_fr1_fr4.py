from app.models import ScanIssueRecord
from app.services.validation_report_service import _delta, _status


def _issue(code: str, severity: str, affected: int, impact: float) -> ScanIssueRecord:
    return ScanIssueRecord(
        scan_id="unit-scan",
        code=code,
        category="Finance",
        title=code,
        severity=severity,
        affected_count=affected,
        premium_only=False,
        recommendation_preview="Review the issue.",
        estimated_impact_eur=impact,
    )


def test_validation_uses_same_five_level_severity_semantics_as_full_and_quick():
    before = _issue("SEV", "critical", 10, 10000.0)
    after = _issue("SEV", "high", 10, 10000.0)
    assert _status(before, after) == "improved"

    delta = _delta(_issue("WARN", "warning", 5, 1000.0), _issue("WARN", "info", 5, 1000.0), "improved")
    assert delta.severity_before == "medium"
    assert delta.severity_after == "info"


def test_validation_severity_regression_detects_critical_transition():
    before = _issue("SEV", "high", 10, 10000.0)
    after = _issue("SEV", "crit", 10, 10000.0)
    assert _status(before, after) == "regressed"
