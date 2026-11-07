from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


REPORT_CONTRACT_VERSION = "executive-report-v1"
FINANCIAL_METHODOLOGY_VERSION = "fin-v1"


class ReportKpi(BaseModel):
    label: str
    value: str
    note: str = ""


class ReportFinding(BaseModel):
    rank: int
    code: str
    title: str
    category: str
    severity: str
    affected_count: int = Field(ge=0)
    estimated_impact_eur: float = 0.0
    recommendation: str


class ReportCategoryScore(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    status: str
    issue_count: int = 0
    affected_count: int = 0


class ReportCategoryImpact(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    issue_count: int = Field(default=0, ge=0)
    affected_count: int = Field(default=0, ge=0)
    estimated_impact_eur: float = Field(default=0.0, ge=0.0)
    impact_share_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    highest_severity: str = "info"


class ReportSeverityBucket(BaseModel):
    label: str
    key: str
    count: int = Field(ge=0)
    percentage: float = 0.0


class ReportPriorityItem(BaseModel):
    priority: str
    focus: str
    impact: str
    effort: str | None = None
    finding_codes: List[str] = Field(default_factory=list)
    recommendation: str


class ReportAppliedException(BaseModel):
    source_exception_entry_no: int
    company_id: str | None = None
    table_id: int
    record_no: str | None = None
    record_caption: str | None = None
    issue_code: str
    reason: str
    exception_created_by: str | None = None
    exception_created_at_utc: datetime | None = None
    captured_at_utc: datetime


class ExecutiveReport(BaseModel):
    contract_version: str = REPORT_CONTRACT_VERSION
    financial_methodology: str = FINANCIAL_METHODOLOGY_VERSION
    report_variant: str = "executive"
    dashboard_mode: str = "read_only"
    report_id: str
    tenant_id: str
    language: str = "en"
    scan_id: str
    scan_type: str = "Manual Scan"
    generated_at_utc: datetime
    scan_generated_at_utc: datetime
    company_label: str
    environment_label: str
    app_version: str = "1.0.0"
    executive_summary: str
    data_health_score: int = Field(ge=0, le=100)
    score_status: str
    total_records: int = Field(ge=0)
    checks_count: int = Field(ge=0)
    checks_total: int = Field(ge=0, default=165)
    issues_count: int = Field(ge=0)
    affected_records: int = Field(ge=0, description="Sum of finding check occurrences; a business record can match multiple checks.")
    applied_exception_count: int = Field(ge=0, default=0)
    estimated_loss_eur: float = 0.0
    potential_saving_eur: float = 0.0
    estimated_premium_price_monthly: float = 0.0
    roi_eur: float = Field(default=0.0, exclude=True, description="Legacy internal metric; never part of public financial report contract.")
    validated_improvement_eur: float | None = None
    realized_saving_eur: float | None = None
    validation_baseline_eligible: bool = True
    validation_baseline_scan_id: str = ""
    exceptions_applied: bool = False
    exception_count: int = Field(default=0, ge=0)
    applied_exceptions: List[ReportAppliedException] = Field(default_factory=list)
    headline: str
    rating: str
    kpis: List[ReportKpi] = Field(default_factory=list)
    all_findings: List[ReportFinding] = Field(default_factory=list)
    top_risks: List[ReportFinding] = Field(default_factory=list)
    quick_wins: List[ReportFinding] = Field(default_factory=list)
    critical_findings: List[ReportFinding] = Field(default_factory=list)
    data_quality: List[ReportCategoryScore] = Field(default_factory=list)
    business_area_impact: List[ReportCategoryImpact] = Field(default_factory=list)
    severity_distribution: List[ReportSeverityBucket] = Field(default_factory=list)
    master_data_quality: List[ReportCategoryScore] = Field(default_factory=list)
    financial_risks: List[ReportFinding] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    priority_matrix: List[ReportPriorityItem] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
