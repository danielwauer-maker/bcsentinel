from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


VALIDATION_REPORT_CONTRACT_VERSION = "validation-report-v1"


class ValidationFindingDelta(BaseModel):
    code: str
    title: str
    category: str
    category_label: str
    severity_before: str | None = None
    severity_after: str | None = None
    affected_before: int = Field(default=0, ge=0)
    affected_after: int = Field(default=0, ge=0)
    impact_before_eur: float = 0.0
    impact_after_eur: float = 0.0
    status: str


class ValidationBusinessAreaDelta(BaseModel):
    name: str
    label: str
    baseline_score: int = Field(ge=0, le=100)
    validation_score: int = Field(ge=0, le=100)
    score_delta: int
    baseline_findings_count: int = Field(default=0, ge=0)
    validation_findings_count: int = Field(default=0, ge=0)
    findings_delta: int
    baseline_affected_records: int = Field(default=0, ge=0)
    validation_affected_records: int = Field(default=0, ge=0)
    affected_records_delta: int
    baseline_estimated_impact_eur: float = 0.0
    validation_estimated_impact_eur: float = 0.0
    estimated_impact_delta_eur: float = 0.0


class ValidationReport(BaseModel):
    contract_version: str = VALIDATION_REPORT_CONTRACT_VERSION
    financial_methodology: str = "fin-v1"
    report_variant: str = "validation"

    report_id: str
    tenant_id: str
    language: str = "en"
    baseline_scan_id: str
    baseline_reference_source: str = "legacy_prior_assessment"
    # V2: keep the permanent initial baseline separate from the previous
    # comparable scan. In v2 baseline_scan_id is the *previous* comparator.
    initial_baseline_scan_id: str | None = None
    initial_baseline_score: int | None = Field(default=None, ge=0, le=100)
    initial_baseline_score_delta: int | None = None
    initial_baseline_scope_version: int | None = None
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
    baseline_affected_records: int = Field(default=0, ge=0)
    validation_affected_records: int = Field(default=0, ge=0)
    affected_records_delta: int = 0

    baseline_estimated_loss_eur: float = 0.0
    validation_estimated_loss_eur: float = 0.0
    estimated_loss_delta_eur: float = 0.0
    business_impact_delta_eur: float = 0.0
    estimated_exposure_reduction_eur: float = 0.0

    resolved_count: int = Field(ge=0)
    improved_count: int = Field(ge=0)
    remaining_count: int = Field(ge=0)
    regressed_count: int = Field(ge=0)
    new_count: int = Field(ge=0)

    executive_summary: str
    management_interpretation: List[str] = Field(default_factory=list)
    business_areas: List[ValidationBusinessAreaDelta] = Field(default_factory=list)
    resolved: List[ValidationFindingDelta] = Field(default_factory=list)
    improved: List[ValidationFindingDelta] = Field(default_factory=list)
    remaining: List[ValidationFindingDelta] = Field(default_factory=list)
    regressed: List[ValidationFindingDelta] = Field(default_factory=list)
    new_findings: List[ValidationFindingDelta] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
