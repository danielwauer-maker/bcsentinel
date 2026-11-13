from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field
from app.schemas.scan_comparison import ScanComparisonEvidence


class MonitoringTrendPoint(BaseModel):
    scan_id: str
    generated_at_utc: datetime
    data_health_score: int = 0
    findings_count: int = 0
    affected_records: int = 0
    modeled_business_impact_eur: float = 0.0


class MonitoringBusinessAreaTrend(BaseModel):
    name: str
    label: str
    baseline_score: int = 0
    previous_score: int = 0
    current_score: int = 0
    score_delta_previous: int = 0
    score_delta_baseline: int = 0
    baseline_findings_count: int = 0
    previous_findings_count: int = 0
    current_findings_count: int = 0
    findings_delta_previous: int = 0
    baseline_impact_eur: float = 0.0
    previous_impact_eur: float = 0.0
    current_impact_eur: float = 0.0
    impact_delta_previous_eur: float = 0.0
    trend: str = "stable"


class MonitoringFindingLifecycle(BaseModel):
    code: str
    title: str
    category: str
    category_label: str
    status: str
    first_seen_at_utc: datetime
    last_seen_at_utc: datetime
    scans_seen: int = 0
    current_severity: str | None = None
    previous_severity: str | None = None
    current_affected_records: int = 0
    previous_affected_records: int = 0
    current_impact_eur: float = 0.0
    previous_impact_eur: float = 0.0


class MonitoringCoverage(BaseModel):
    period_start_utc: datetime
    period_end_utc: datetime
    scans_in_period: int = 0
    latest_scan_at_utc: datetime
    previous_scan_at_utc: datetime | None = None
    baseline_scan_at_utc: datetime
    freshness_hours: float = 0.0
    monitoring_access_until: str | None = None
    data_freshness: str = "current"


class MonitoringReport(BaseModel):
    contract_version: str = "monitoring-report-v1"
    report_variant: str = "monitoring"
    comparison_evidence: ScanComparisonEvidence | None = None
    tenant_id: str
    company_name: str
    environment_name: str
    language: str = "en"

    current_scan_id: str
    previous_scan_id: str | None = None
    baseline_scan_id: str

    current_data_health_score: int = 0
    previous_data_health_score: int = 0
    baseline_data_health_score: int = 0
    score_delta_previous: int = 0
    score_delta_baseline: int = 0

    current_findings_count: int = 0
    previous_findings_count: int = 0
    findings_delta_previous: int = 0

    current_affected_records: int = 0
    previous_affected_records: int = 0
    affected_records_delta_previous: int = 0

    current_business_impact_eur: float = 0.0
    previous_business_impact_eur: float = 0.0
    business_impact_delta_previous_eur: float = 0.0
    business_impact_delta_baseline_eur: float = 0.0

    current_critical_findings: int = 0
    current_high_findings: int = 0

    trend_points: list[MonitoringTrendPoint] = Field(default_factory=list)
    business_areas: list[MonitoringBusinessAreaTrend] = Field(default_factory=list)
    finding_lifecycle: list[MonitoringFindingLifecycle] = Field(default_factory=list)

    new_findings_count: int = 0
    resolved_findings_count: int = 0
    persistent_findings_count: int = 0
    improving_findings_count: int = 0
    regressing_findings_count: int = 0
    reopened_findings_count: int = 0

    top_priorities: list[MonitoringFindingLifecycle] = Field(default_factory=list)
    management_interpretation: list[str] = Field(default_factory=list)
    coverage: MonitoringCoverage
