from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


FREE_HEALTH_REPORT_CONTRACT_VERSION = "free-health-report-v1"


class FreeRiskArea(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    status: str
    issue_count: int = Field(default=0, ge=0)
    affected_records: int = Field(default=0, ge=0)
    highest_severity: str = "info"


class FreeSeveritySummary(BaseModel):
    critical: int = Field(default=0, ge=0)
    high: int = Field(default=0, ge=0)
    medium: int = Field(default=0, ge=0)
    low: int = Field(default=0, ge=0)
    info: int = Field(default=0, ge=0)


class FreeHealthReport(BaseModel):
    """Aggregate-only report contract for Free Entry.

    Deliberately excludes finding titles, issue codes, recommendations, root
    causes, record-level data and concrete financial values.
    """

    contract_version: str = FREE_HEALTH_REPORT_CONTRACT_VERSION
    report_variant: str = "free_health"
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

    severity: FreeSeveritySummary
    risk_areas: List[FreeRiskArea] = Field(default_factory=list)
    impact_band: str
    summary: str
    upgrade_message: str
