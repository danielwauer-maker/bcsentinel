"""Versioned source-record identity envelope for gated scan-sync ingestion.

This module validates client-declared shape, canonical bytes and exact scope
values passed by the leased scan-sync adapter. It cannot by itself prove BC
source provenance or a stable source snapshot under concurrent data changes.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError


class SourceRecordIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    table_id: Literal[18]  # BC Customer
    record_system_id: UUID

    @model_validator(mode="after")
    def nonzero_system_id(self):
        if self.record_system_id.int == 0:
            raise PydanticCustomError("record_identity", "business-record SystemId must not be empty")
        return self


class SourceRecordEvidenceV1(BaseModel):
    """Complete identity membership for one *supported* source check only."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["bc-record-evidence-v1"]
    tenant_id: str = Field(min_length=1, max_length=50)
    scan_id: str = Field(min_length=1, max_length=50)
    company_id: UUID
    check_code: Literal["CUSTOMERS_DUPLICATE_VAT"]
    observed_at_utc: datetime
    completed: Literal[True]
    affected_records_count: int = Field(ge=0, le=2000)
    records: tuple[SourceRecordIdentity, ...] = Field(max_length=2000)

    @model_validator(mode="after")
    def complete_nonduplicated_membership(self):
        if self.company_id.int == 0:
            raise PydanticCustomError("record_company", "company_id cannot be empty")
        if self.observed_at_utc.utcoffset() != timedelta(0):
            raise PydanticCustomError("record_time", "observed_at_utc must use UTC")
        if len(self.records) != self.affected_records_count:
            raise PydanticCustomError("record_coverage", "record count and observed members disagree")
        identities = [record.record_system_id for record in self.records]
        if len(set(identities)) != len(identities):
            raise PydanticCustomError("record_duplicate", "duplicate business-record SystemId")
        # A VAT duplicate check produces group members, never a singleton.
        if self.affected_records_count == 1:
            raise PydanticCustomError("record_membership", "a single record is not a duplicate group")
        return self


def canonical_record_evidence(envelope: SourceRecordEvidenceV1) -> tuple[str, str]:
    """Canonical JSON + SHA-256 for immutable-storage preparation only.

    Hashing provides deterministic corruption detection, NOT proof that AL,
    an authorized tenant, or a BC execution lease produced these records.
    """
    body = envelope.model_dump(mode="json")
    body["company_id"] = str(envelope.company_id)
    body["records"] = sorted(
        body["records"],
        key=lambda item: (item["table_id"], item["record_system_id"]),
    )
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    if len(canonical.encode("utf-8")) > 250_000:
        raise ValueError("record evidence exceeds storage budget")
    return canonical, hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_record_evidence_contract(
    envelope: SourceRecordEvidenceV1,
    *,
    tenant_id: str,
    scan_id: str,
    company_id: str,
    check_status: str,
    group_finding_count: int,
    affected_records_count: int,
) -> tuple[str, str]:
    """Require exact trusted binding values provided by a future sync adapter.

    The caller must separately verify registered company, sealed expectation,
    original lease and immutable scan lifecycle before trusting these values.
    """
    try:
        verified_company = UUID(company_id)
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("invalid bound company") from exc
    if (envelope.tenant_id != tenant_id or envelope.scan_id != scan_id
            or verified_company.int == 0 or envelope.company_id != verified_company):
        raise ValueError("record evidence scope mismatch")
    if check_status == "PASS":
        if group_finding_count != 0 or affected_records_count != 0:
            raise ValueError("PASS cannot have record members or findings")
    elif check_status == "FINDINGS":
        if group_finding_count <= 0 or affected_records_count < 2:
            raise ValueError("FINDINGS requires observed multi-record groups")
    else:
        raise ValueError("incomplete or skipped check cannot attest records")
    if envelope.affected_records_count != affected_records_count:
        raise ValueError("record membership differs from source findings")
    return canonical_record_evidence(envelope)
