from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


QUICK_ASSESSMENT_REPORT_CONTRACT_VERSION = "quick-assessment-report-v1"


class QuickSeveritySummary(BaseModel):
    """Same normalized five-level severity vocabulary used by the Data Health scan."""

    critical: int = Field(default=0, ge=0)
    high: int = Field(default=0, ge=0)
    medium: int = Field(default=0, ge=0)
    low: int = Field(default=0, ge=0)
    info: int = Field(default=0, ge=0)


class QuickRiskArea(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    status: str
    issue_count: int = Field(default=0, ge=0)
    affected_records: int = Field(default=0, ge=0)
    highest_severity: str = "info"


class QuickFinding(BaseModel):
    """Quick-safe finding shape.

    Deliberately incapable of carrying issue codes, record-level detail,
    root-cause catalogues, recommendation previews or exact financial values.
    Rank is structurally limited to the Quick Assessment Top-5 boundary. The
    impact band is a non-monetary disclosure derived server-side from the same
    internal modeled signal that helps prioritize Full Assessment findings.
    """

    rank: int = Field(ge=1, le=5)
    title: str
    severity: str
    affected_count: int = Field(default=0, ge=0)
    risk_area: str
    impact_band: str
    next_action: str


class QuickAssessmentReport(BaseModel):
    """Limited paid report between Free Health and Full Assessment.

    The report is intentionally narrower than Executive/Assessment. Exact EUR
    values, issue codes, root causes, record drilldowns and full remediation
    worklists are absent from the schema, not merely hidden in presentation.
    The schema itself rejects more than five findings.
    """

    contract_version: str = QUICK_ASSESSMENT_REPORT_CONTRACT_VERSION
    report_variant: str = "quick_assessment"
    report_id: str
    tenant_id: str
    language: str = "en"
    scan_id: str
    generated_at_utc: datetime
    scan_generated_at_utc: datetime
    company_label: str
    environment_label: str

    data_health_score: int = Field(ge=0, le=100)
    score_status: str
    checks_count: int = Field(default=0, ge=0)
    modules_analyzed: int = Field(default=0, ge=0)
    issues_count: int = Field(default=0, ge=0)
    affected_records: int = Field(default=0, ge=0)
    total_records: int = Field(default=0, ge=0)

    severity: QuickSeveritySummary
    risk_areas: List[QuickRiskArea] = Field(default_factory=list)
    impact_band: str
    management_interpretation: str
    findings: List[QuickFinding] = Field(default_factory=list, max_length=5)
    # Retained for API compatibility. The final two-page report does not render
    # this generic list because each Top-5 finding already owns its Next Action.
    recommended_next_actions: List[str] = Field(default_factory=list)
    upgrade_message: str
