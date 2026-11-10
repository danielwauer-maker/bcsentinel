"""Read-only verifier for persisted BC record identity evidence.

This deliberately does not grant Validation/Monitoring finding transitions:
VAT duplicate *group membership* is not a stable individual issue identity.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone

from pydantic import ValidationError
from sqlalchemy import select

from app.models import (
    Scan, ScanExecutionEvidence, ScanExpectationSnapshot, ScanIssueRecord,
    ScanRecordIdentityEvidence, ScanRunStatus, Tenant,
)
from app.services.scan_company_service import canonical_company_id
from app.services.source_record_evidence_contract import (
    SourceRecordEvidenceV1, canonical_record_evidence,
    validate_record_evidence_contract,
)

SUPPORTED_CHECK = "CUSTOMERS_DUPLICATE_VAT"


def _utc(value: datetime) -> datetime:
    if not isinstance(value, datetime):
        raise ValueError("missing lifecycle timestamp")
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def read_verified_record_membership(db, tenant_id: str, scan_id: str) -> SourceRecordEvidenceV1 | None:
    """Fail closed unless the database row agrees with finalized source scope.

    The returned object is only evidence of *reported members*. Caller must
    still establish true BC source completeness and pairwise group semantics.
    """
    scan = db.scalar(select(Scan).where(Scan.tenant_id == tenant_id, Scan.scan_id == scan_id))
    run = db.scalar(select(ScanRunStatus).where(ScanRunStatus.tenant_id == tenant_id, ScanRunStatus.run_id == scan_id))
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
    stored = db.get(ScanRecordIdentityEvidence, (scan_id, SUPPORTED_CHECK))
    start = db.get(ScanExpectationSnapshot, scan_id)
    executed = db.get(ScanExecutionEvidence, scan_id)
    if any(row is None for row in (scan, run, tenant, stored, start, executed)):
        return None
    try:
        company = canonical_company_id(tenant.bc_company_id)
        if (scan.scan_type != "deep" or run.status != "completed"
                or not scan.lcy_code
                or any(canonical_company_id(row.company_id) != company for row in (scan, stored, start, executed))
                or any(row.tenant_id != tenant_id for row in (scan, run, stored, start, executed))
                or stored.schema_version != "bc-record-evidence-v1"
                or stored.check_code != SUPPORTED_CHECK
                or executed.schema_version != "bc-check-execution-partial-v1"):
            return None
        for row in (stored, start, executed):
            if hashlib.sha256(row.payload_json.encode("utf-8")).hexdigest() != row.payload_sha256:
                return None
        frozen, checks = json.loads(start.payload_json), json.loads(executed.payload_json)
        if (frozen.get("schema_version") != "bc-scan-expectation-v2"
                or frozen.get("scan_id") != scan_id or frozen.get("tenant_id") != tenant_id
                or canonical_company_id(frozen.get("company_id")) != company
                or frozen.get("environment") != (tenant.environment_name or "").strip()
                or frozen.get("currency") != scan.lcy_code
                or not isinstance(frozen.get("exception_scope"), list)
                or checks.get("schema_version") != "bc-check-execution-partial-v1"):
            return None
        selected = [c for c in frozen["checks"] if c["code"] == SUPPORTED_CHECK]
        observation = [c for c in checks["checks"] if c["code"] == SUPPORTED_CHECK]
        if (len(selected) != 1 or selected[0]["enabled"] is not True or len(observation) != 1
                or selected[0]["module"] != "CUSTOMER"):
            return None
        check = observation[0]
        if check["status"] not in ("PASS", "FINDINGS"):
            return None
        if len({c["code"] for c in checks["checks"]}) != len(checks["checks"]):
            return None
        issues = db.scalars(select(ScanIssueRecord).where(
            ScanIssueRecord.scan_id == scan_id, ScanIssueRecord.code == SUPPORTED_CHECK,
        )).all()
        if check["finding_count"] != len(issues):
            return None
        affected = sum(i.affected_count for i in issues)
        if any(i.affected_count < 2 for i in issues):
            return None
        envelope = SourceRecordEvidenceV1.model_validate_json(stored.payload_json)
        canonical, digest = validate_record_evidence_contract(
            envelope, tenant_id=tenant_id, scan_id=scan_id,
            company_id=company, check_status=check["status"],
            group_finding_count=len(issues), affected_records_count=affected,
        )
        if canonical != stored.payload_json or digest != stored.payload_sha256:
            return None
        accepted = _utc(start.created_at_utc)
        started, persisted, completed = (
            _utc(run.started_at_utc), _utc(run.result_persisted_at_utc), _utc(run.completed_at_utc)
        )
        observed = _utc(envelope.observed_at_utc)
        check_at = _utc(datetime.fromisoformat(check["observed_at_utc"].replace("Z", "+00:00")))
        stored_at = _utc(stored.created_at_utc)
        if not (accepted <= started <= observed <= check_at <= persisted <= completed):
            return None
        if not (persisted <= stored_at <= completed + timedelta(minutes=5)):
            # The ORM inserts the record after the terminal state is assigned,
            # but within the same database transaction; allow a narrow window.
            return None
        return envelope
    except (ValueError, TypeError, KeyError, AttributeError, IndexError, ValidationError):
        return None
