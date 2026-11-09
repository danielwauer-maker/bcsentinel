from pydantic import BaseModel, Field


class ScanComparisonEvidence(BaseModel):
    comparable: bool = False
    reason_codes: list[str] = Field(default_factory=list)
    comparable_checks: list[str] = Field(default_factory=list)
    health_score_comparable: bool = False
    impact_comparable: bool = False
