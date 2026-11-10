"""Fail-closed comparison contract for independently verified scan evidence.

This module does not establish that submitted evidence is authentic or immutable.
Only a trusted persistence/verification layer may set ``source_verified``. Legacy
scans, and callers without such a layer, must be passed as unverified.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib
import json
import re
from uuid import UUID

from app.services.scan_company_service import canonical_company_id


class CheckStatus(str, Enum):
    PASS = "PASS"
    FINDINGS = "FINDINGS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    NOT_EXECUTED = "NOT_EXECUTED"


class Reason(str, Enum):
    MISSING_PROVENANCE = "MISSING_PROVENANCE"
    TENANT_MISMATCH = "TENANT_MISMATCH"
    COMPANY_MISMATCH = "COMPANY_MISMATCH"
    ENVIRONMENT_MISMATCH = "ENVIRONMENT_MISMATCH"
    CURRENCY_MISMATCH = "CURRENCY_MISMATCH"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"
    METHODOLOGY_MISMATCH = "METHODOLOGY_MISMATCH"
    CATALOG_MISMATCH = "CATALOG_MISMATCH"
    INCOMPLETE_CHECK_COVERAGE = "INCOMPLETE_CHECK_COVERAGE"
    UNSTABLE_FINDING_IDENTITY = "UNSTABLE_FINDING_IDENTITY"
    INVALID_SCAN_ORDER = "INVALID_SCAN_ORDER"
    SAME_SCAN = "SAME_SCAN"


@dataclass(frozen=True)
class CheckEvidence:
    code: str
    status: CheckStatus
    # True only if the source proved identities for every finding of this check.
    stable_finding_identities: bool = False


@dataclass(frozen=True)
class ScanEvidence:
    tenant_id: str
    scan_id: str
    company_id: str
    environment: str
    currency: str
    methodology_version: str
    catalog_version: str
    catalog_fingerprint: str
    modules: tuple[str, ...]
    expected_checks: tuple[str, ...]
    checks: tuple[CheckEvidence, ...]
    completed_at: datetime
    result_persisted_at: datetime
    scan_status: str
    source_verified: bool = False


@dataclass(frozen=True)
class ComparisonResult:
    comparable: bool
    reasons: tuple[Reason, ...]
    comparable_checks: tuple[str, ...]
    health_score_comparable: bool
    impact_comparable: bool


def _canonical_names(values: tuple[str, ...]) -> tuple[str, ...]:
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError("names must be nonempty strings")
    result = tuple(sorted(value.strip().upper() for value in values))
    if len(set(result)) != len(result):
        raise ValueError("duplicate names")
    return result


def catalog_fingerprint(catalog_version: str, methodology_version: str, checks: tuple[tuple[str, str], ...]) -> str:
    """Hash a versioned code/module catalog independently of its input order."""
    if not catalog_version.strip() or not methodology_version.strip():
        raise ValueError("catalog and methodology versions are required")
    normalized = [(code.strip().upper(), module.strip().upper()) for code, module in checks]
    if not normalized or any(not code or not module for code, module in normalized):
        raise ValueError("catalog entries must be nonempty")
    if len({code for code, _ in normalized}) != len(normalized):
        raise ValueError("duplicate check code")
    body = {"contract": "bcs-check-catalog-v1", "catalog_version": catalog_version.strip(),
            "methodology_version": methodology_version.strip(), "checks": sorted(normalized)}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def finding_comparison_identity(*, tenant_id: str, company_id: str, check_code: str,
                                methodology_version: str, module_code: str, finding_type: str, criterion: str,
                                record_system_id: str | None) -> str | None:
    """Use the affected BC record's stable SystemId, never the finding row's SystemId.

    No fallback is invented for aggregate or multi-record findings. A changed or
    recreated record has a different SystemId and therefore a different identity.
    """
    if not all(str(value or "").strip() for value in (tenant_id, check_code, methodology_version, module_code, finding_type, criterion, record_system_id)):
        return None
    try:
        company = canonical_company_id(company_id)
        record = UUID(str(record_system_id).strip().strip("{}"))
        if record.int == 0:
            return None
    except (ValueError, TypeError, AttributeError):
        return None
    body = ["bcs-finding-comparison-v1", tenant_id.strip(), company, check_code.strip().upper(),
            methodology_version.strip(), module_code.strip().upper(), finding_type.strip(), criterion.strip(), str(record)]
    raw = json.dumps(body, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def compare_scans(previous: ScanEvidence | None, current: ScanEvidence | None) -> ComparisonResult:
    reasons: set[Reason] = set()
    comparable_checks: set[str] = set()
    if previous is None or current is None or previous.source_verified is not True or current.source_verified is not True:
        return ComparisonResult(False, (Reason.MISSING_PROVENANCE,), (), False, False)
    required_fields = ("tenant_id", "scan_id", "company_id", "environment", "currency", "methodology_version", "catalog_version", "catalog_fingerprint")
    if any(not isinstance(getattr(scan, field, None), str) for scan in (previous, current) for field in required_fields):
        return ComparisonResult(False, (Reason.MISSING_PROVENANCE,), (), False, False)
    if not previous.tenant_id.strip() or previous.tenant_id != current.tenant_id:
        reasons.add(Reason.TENANT_MISMATCH)
    if not previous.scan_id.strip() or not current.scan_id.strip():
        reasons.add(Reason.MISSING_PROVENANCE)
    elif previous.scan_id == current.scan_id:
        reasons.add(Reason.SAME_SCAN)
    try:
        if canonical_company_id(previous.company_id) != canonical_company_id(current.company_id):
            reasons.add(Reason.COMPANY_MISMATCH)
    except ValueError:
        reasons.add(Reason.MISSING_PROVENANCE)
    if not previous.environment.strip() or not current.environment.strip():
        reasons.add(Reason.MISSING_PROVENANCE)
    elif previous.environment != current.environment:
        reasons.add(Reason.ENVIRONMENT_MISMATCH)
    if not previous.currency.strip() or not current.currency.strip():
        reasons.add(Reason.MISSING_PROVENANCE)
    elif previous.currency.upper() != current.currency.upper():
        reasons.add(Reason.CURRENCY_MISMATCH)
    if not previous.methodology_version.strip() or not current.methodology_version.strip():
        reasons.add(Reason.MISSING_PROVENANCE)
    elif previous.methodology_version != current.methodology_version:
        reasons.add(Reason.METHODOLOGY_MISMATCH)
    if (not previous.catalog_version.strip() or not current.catalog_version.strip()
            or not re.fullmatch(r"[0-9a-f]{64}", previous.catalog_fingerprint)
            or not re.fullmatch(r"[0-9a-f]{64}", current.catalog_fingerprint)):
        reasons.add(Reason.MISSING_PROVENANCE)
    elif (previous.catalog_version, previous.catalog_fingerprint) != (current.catalog_version, current.catalog_fingerprint):
        reasons.add(Reason.CATALOG_MISMATCH)
    if (not isinstance(previous.completed_at, datetime) or not isinstance(current.completed_at, datetime)
            or previous.completed_at.utcoffset() is None or current.completed_at.utcoffset() is None
            or previous.completed_at >= current.completed_at):
        reasons.add(Reason.INVALID_SCAN_ORDER)
    scan_complete = not (previous.scan_status != "completed" or current.scan_status != "completed"
            or not isinstance(previous.result_persisted_at, datetime) or not isinstance(current.result_persisted_at, datetime)
            or previous.result_persisted_at.utcoffset() is None or current.result_persisted_at.utcoffset() is None)
    if not scan_complete:
        reasons.add(Reason.INCOMPLETE_CHECK_COVERAGE)
    try:
        old_modules, new_modules = _canonical_names(previous.modules), _canonical_names(current.modules)
        old_checks, new_checks = _canonical_names(previous.expected_checks), _canonical_names(current.expected_checks)
        if not old_modules or not new_modules or not old_checks or not new_checks:
            reasons.add(Reason.MISSING_PROVENANCE)
        if old_modules != new_modules or old_checks != new_checks:
            reasons.add(Reason.SCOPE_MISMATCH)
        old_codes = _canonical_names(tuple(item.code for item in previous.checks))
        new_codes = _canonical_names(tuple(item.code for item in current.checks))
        old_map = {item.code.strip().upper(): item for item in previous.checks}
        new_map = {item.code.strip().upper(): item for item in current.checks}
        if old_codes != old_checks or new_codes != new_checks:
            reasons.add(Reason.INCOMPLETE_CHECK_COVERAGE)
        for code in set(old_checks) & set(new_checks):
            a, b = old_map.get(code), new_map.get(code)
            if a is None or b is None or a.status not in {CheckStatus.PASS, CheckStatus.FINDINGS} or b.status not in {CheckStatus.PASS, CheckStatus.FINDINGS}:
                reasons.add(Reason.INCOMPLETE_CHECK_COVERAGE)
                continue
            if (a.status == CheckStatus.FINDINGS and a.stable_finding_identities is not True) or (b.status == CheckStatus.FINDINGS and b.stable_finding_identities is not True):
                reasons.add(Reason.UNSTABLE_FINDING_IDENTITY)
                continue
            comparable_checks.add(code)
    except (ValueError, AttributeError, TypeError):
        reasons.add(Reason.MISSING_PROVENANCE)
    # Tenant/company/environment/methodology/catalog mismatches invalidate every
    # per-check comparison, even if an individual check name happens to match.
    if not scan_complete or reasons & {Reason.TENANT_MISMATCH, Reason.COMPANY_MISMATCH, Reason.ENVIRONMENT_MISMATCH, Reason.CURRENCY_MISMATCH, Reason.SCOPE_MISMATCH,
                  Reason.METHODOLOGY_MISMATCH, Reason.CATALOG_MISMATCH, Reason.MISSING_PROVENANCE,
                  Reason.INVALID_SCAN_ORDER, Reason.SAME_SCAN}:
        comparable_checks.clear()
    ok = not reasons
    # A catalog match alone does not prove score weights or impact model versions.
    return ComparisonResult(ok, tuple(sorted(reasons, key=lambda reason: reason.value)),
                            tuple(sorted(comparable_checks)), False, False)


def _verified_clean_scan(db, tenant_id: str, scan_id: str) -> tuple[ScanEvidence, str] | None:
    """Read only genuinely completed *zero-finding* runs from sealed v2 evidence.

    This intentionally does not attest row-level finding identities, aggregate
    changes, health scores, impact or historical/partial evidence.
    """
    from datetime import timezone
    from sqlalchemy import select
    from app.models import (
        Scan, ScanExecutionEvidence, ScanExpectationSnapshot, ScanIssueRecord,
        ScanRunStatus, Tenant,
    )
    from app.services.scan_catalog_contract import (
        CHECK_MODULE_TO_RUN_MODULE, SUPPORTED_METHODOLOGIES, catalog_1_0_2_57,
    )

    def utc(value):
        if not isinstance(value, datetime):
            raise ValueError("missing timestamp")
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)

    scan = db.scalar(select(Scan).where(Scan.scan_id == scan_id, Scan.tenant_id == tenant_id))
    run = db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == scan_id, ScanRunStatus.tenant_id == tenant_id))
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
    expectation = db.get(ScanExpectationSnapshot, scan_id)
    observed = db.get(ScanExecutionEvidence, scan_id)
    if any(value is None for value in (scan, run, tenant, expectation, observed)):
        return None
    try:
        company = canonical_company_id(tenant.bc_company_id)
        if (scan.scan_type != "deep" or run.status != "completed"
                or scan.issues_count != 0
                or canonical_company_id(scan.bc_company_id) != company
                or canonical_company_id(expectation.company_id) != company
                or canonical_company_id(observed.company_id) != company
                or any(row.tenant_id != tenant_id for row in (scan, run, expectation, observed))
                or not scan.lcy_code
                or db.scalar(select(ScanIssueRecord.id).where(ScanIssueRecord.scan_id == scan_id).limit(1)) is not None):
            return None
        if (hashlib.sha256(expectation.payload_json.encode("utf-8")).hexdigest() != expectation.payload_sha256
                or hashlib.sha256(observed.payload_json.encode("utf-8")).hexdigest() != observed.payload_sha256
                or observed.schema_version != "bc-check-execution-partial-v1"):
            return None
        frozen = json.loads(expectation.payload_json)
        executed = json.loads(observed.payload_json)
        if (frozen.get("schema_version") != "bc-scan-expectation-v2"
                or frozen.get("scan_id") != scan_id or frozen.get("tenant_id") != tenant_id
                or canonical_company_id(frozen.get("company_id")) != company
                or frozen.get("environment") != (tenant.environment_name or "").strip()
                or frozen.get("currency") != scan.lcy_code
                or not isinstance(frozen.get("exception_scope"), list)
                or executed.get("schema_version") != observed.schema_version):
            return None

        catalog_version, _, catalog = catalog_1_0_2_57()
        declared = frozen["checks"]
        declared_pairs = tuple((item["code"], item["module"]) for item in declared)
        if (len(declared_pairs) != len(catalog)
                or frozenset(declared_pairs) != catalog
                or frozen["catalog_version"] != catalog_version
                or frozen["methodology_version"] not in SUPPORTED_METHODOLOGIES
                or frozen["catalog_fingerprint"] != catalog_fingerprint(
                    frozen["catalog_version"], frozen["methodology_version"], declared_pairs)):
            return None
        modules = _canonical_names(tuple(frozen["modules"]))
        expected = _canonical_names(tuple(item["code"] for item in declared if item["enabled"]))
        if (not modules or not expected
                or any(item["enabled"] and CHECK_MODULE_TO_RUN_MODULE[item["module"]] not in modules for item in declared)
                or scan.checks_count != len(expected)):
            return None

        observations = executed["checks"]
        codes = _canonical_names(tuple(item["code"] for item in observations))
        if len(codes) != len(observations):
            return None
        statuses = {item["code"]: item for item in observations}
        if not set(expected).issubset(statuses):
            return None

        accepted_at = utc(expectation.created_at_utc)
        started_at, stored_at, completed_at = (
            utc(run.started_at_utc), utc(run.result_persisted_at_utc), utc(run.completed_at_utc)
        )
        if not (accepted_at <= started_at <= stored_at <= completed_at):
            return None
        if not (started_at <= utc(observed.created_at_utc) <= completed_at):
            return None
        for code, item in statuses.items():
            if not (started_at <= utc(datetime.fromisoformat(item["observed_at_utc"].replace("Z", "+00:00"))) <= stored_at):
                return None
            if code in expected:
                if item["status"] != "PASS" or item["finding_count"] != 0:
                    return None
            elif item["status"] != "SKIPPED" or item["finding_count"] != 0:
                return None
        if set(statuses) - {item["code"] for item in declared}:
            return None
        if scan.generated_at_utc is None:
            return None
        # Frozen exception scope is independently compared across both scans.
        scope_key = json.dumps(frozen["exception_scope"], sort_keys=True, separators=(",", ":"))
        return ScanEvidence(
            tenant_id=tenant_id, scan_id=scan_id, company_id=company,
            environment=frozen["environment"], currency=frozen["currency"],
            methodology_version=frozen["methodology_version"],
            catalog_version=frozen["catalog_version"],
            catalog_fingerprint=frozen["catalog_fingerprint"],
            modules=modules, expected_checks=expected,
            checks=tuple(CheckEvidence(code, CheckStatus.PASS) for code in expected),
            completed_at=completed_at, result_persisted_at=stored_at,
            scan_status="completed", source_verified=True,
        ), scope_key
    except (KeyError, ValueError, TypeError, AttributeError, IndexError):
        return None


def compare_persisted_scans(db, tenant_id: str, previous_scan_id: str | None, current_scan_id: str) -> ComparisonResult:
    """Narrow positive path for fully evidenced clean checks, fail-closed otherwise.

    No finding transitions, score deltas or impact deltas are authorized here.
    Do not remove Validation/Monitoring export guards on this basis.
    """
    if not previous_scan_id or not current_scan_id:
        return compare_scans(None, None)
    previous = _verified_clean_scan(db, tenant_id, previous_scan_id)
    current = _verified_clean_scan(db, tenant_id, current_scan_id)
    if previous is None or current is None:
        return compare_scans(None, None)
    if previous[1] != current[1]:
        return ComparisonResult(False, (Reason.SCOPE_MISMATCH,), (), False, False)
    return compare_scans(previous[0], current[0])
