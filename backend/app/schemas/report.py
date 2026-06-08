from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


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


class ReportPriorityItem(BaseModel):
    priority: str
    focus: str
    impact: str
    effort: str
    recommendation: str


class ExecutiveReport(BaseModel):
    report_id: str
    tenant_id: str
    language: str = "en"
    scan_id: str
    generated_at_utc: datetime
    scan_generated_at_utc: datetime
    company_label: str
    environment_label: str
    executive_summary: str
    data_health_score: int = Field(ge=0, le=100)
    score_status: str
    total_records: int = Field(ge=0)
    checks_count: int = Field(ge=0)
    issues_count: int = Field(ge=0)
    affected_records: int = Field(ge=0)
    estimated_loss_eur: float = 0.0
    potential_saving_eur: float = 0.0
    estimated_premium_price_monthly: float = 0.0
    roi_eur: float = 0.0
    headline: str
    rating: str
    kpis: List[ReportKpi] = Field(default_factory=list)
    top_risks: List[ReportFinding] = Field(default_factory=list)
    quick_wins: List[ReportFinding] = Field(default_factory=list)
    critical_findings: List[ReportFinding] = Field(default_factory=list)
    data_quality: List[ReportCategoryScore] = Field(default_factory=list)
    master_data_quality: List[ReportCategoryScore] = Field(default_factory=list)
    financial_risks: List[ReportFinding] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    priority_matrix: List[ReportPriorityItem] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
