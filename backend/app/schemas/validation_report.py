from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


VALIDATION_REPORT_CONTRACT_VERSION = "validation-report-v1"


class ValidationFindingDelta(BaseModel):
    code: str
    title: str
    category: str
    severity_before: str | None = None
    severity_after: str | None = None
    affected_before: int = Field(default=0, ge=0)
    affected_after: int = Field(default=0, ge=0)
    impact_before_eur: float = 0.0
    impact_after_eur: float = 0.0
    status: str


class ValidationReport(BaseModel):
    contract_version: str = VALIDATION_REPORT_CONTRACT_VERSION
    financial_methodology: str = "fin-v1"
    report_variant: str = "validation"

    report_id: str
    tenant_id: str
    language: str = "en"
    baseline_scan_id: str
    validation_scan_id: str
    generated_at_utc: datetime
    baseline_generated_at_utc: datetime
    validation_generated_at_utc: datetime
    company_label: str
    environment_label: str

    baseline_score: int = Field(ge=0, le=100)
    validation_score: int = Field(ge=0, le=100)
    score_delta: int
    baseline_issues_count: int = Field(ge=0)
    validation_issues_count: int = Field(ge=0)
    issues_delta: int

    baseline_estimated_loss_eur: float = 0.0
    validation_estimated_loss_eur: float = 0.0
    estimated_loss_delta_eur: float = 0.0
    estimated_exposure_reduction_eur: float = 0.0

    resolved_count: int = Field(ge=0)
    improved_count: int = Field(ge=0)
    remaining_count: int = Field(ge=0)
    regressed_count: int = Field(ge=0)
    new_count: int = Field(ge=0)

    executive_summary: str
    resolved: List[ValidationFindingDelta] = []
    improved: List[ValidationFindingDelta] = []
    remaining: List[ValidationFindingDelta] = []
    regressed: List[ValidationFindingDelta] = []
    new_findings: List[ValidationFindingDelta] = []
    next_steps: List[str] = []
