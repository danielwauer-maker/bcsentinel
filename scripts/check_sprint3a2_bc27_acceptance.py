#!/usr/bin/env python3
"""Offline fail-closed BC27 Sprint 3A.2 acceptance evidence validator.

No secrets, network access, server mutations, or simulated BC runtime.
Exit 0 means complete, consistently documented evidence, NOT independent proof
that screenshots/links were genuine or that a real runtime test was executed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from uuid import UUID

EXPECTED_IDS = tuple(f"BC27-{n:02d}" for n in range(1, 9))
REQUIRED_GATES = (
    "al_compile", "backend_regression", "migration_0040", "upgrade_bc27",
    "non_super", "real_two_scans", "tenant_isolation", "retries", "reports_still_locked",
)
REQUIRED_ROLES = (
    "scan_user_non_super", "viewer_read_only", "setup_role",
    "scheduler_role", "admin_role",
)
STATUSES = {"NOT_EXECUTED", "PASS", "FAIL", "BLOCKED"}
SHA = re.compile(r"^[0-9a-f]{40}$")
PACKAGE_SHA = re.compile(r"^[0-9a-f]{64}$")
REDACTION_RISKS = (
    re.compile(r"(?i)\b(?:x-api-token|authorization|bearer|secret_key|api_token|password)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\b(?:customer_email|vat_registration_no|vat_number)\s*[:=]\s*\S+"),
)


def evaluate(record: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["Acceptance evidence must be a JSON object."]
    if record.get("schema_version") != "bcs-sprint3a2-bc27-acceptance-v1":
        errors.append("Unrecognized evidence schema version.")
    if record.get("pr_number") != 162 or record.get("repository") != "danielwauer-maker/bcsentinel":
        errors.append("Acceptance evidence references the wrong repository or PR.")
    if record.get("extension_version") != "1.0.2.58" or record.get("backend_revision") != "0040_scan_record_identity_evidence":
        errors.append("Incorrect frozen extension/backend revision.")
    if not SHA.fullmatch(str(record.get("head_sha") or "")):
        errors.append("Missing exact immutable 40-character tested GitHub HEAD.")
    context = record.get("run_context") or {}
    if not isinstance(context, dict):
        context = {}
        errors.append("Missing run context.")
    for field in ("bc_version", "sandbox_environment", "backend_commit_sha", "utc_started_at", "utc_finished_at"):
        if not isinstance(context.get(field), str) or not context[field].strip():
            errors.append(f"Missing run_context.{field}.")
    if not SHA.fullmatch(str(context.get("backend_commit_sha") or "")):
        errors.append("Missing exact backend commit SHA.")
    if not PACKAGE_SHA.fullmatch(str(context.get("extension_package_sha256") or "")):
        errors.append("Missing SHA-256 of installed .app artifact.")
    try:
        if UUID(str(context.get("company_id") or "")).int == 0:
            raise ValueError()
    except (TypeError, ValueError, AttributeError):
        errors.append("Missing valid nonzero BC Company GUID.")
    roles = record.get("roles") or {}
    if not isinstance(roles, dict):
        roles = {}
        errors.append("Invalid roles object.")
    for role in REQUIRED_ROLES:
        if roles.get(role) != "PASS":
            errors.append(f"Role {role} not passed.")
    gates = record.get("gates") or {}
    if not isinstance(gates, dict):
        gates = {}
        errors.append("Invalid gates object.")
    for gate in REQUIRED_GATES:
        if gates.get(gate) != "PASS":
            errors.append(f"Gate {gate} not passed.")
    scenarios = record.get("scenarios")
    if not isinstance(scenarios, list):
        scenarios = []
        errors.append("Missing scenarios.")
    ids = [str(case.get("id")) for case in scenarios if isinstance(case, dict)]
    if sorted(ids) != list(EXPECTED_IDS):
        errors.append("Exactly eight distinct BC27-01..08 scenarios are required.")
    for case in scenarios:
        if not isinstance(case, dict):
            errors.append("Scenario is not an object.")
            continue
        sid = str(case.get("id"))
        if case.get("status") not in STATUSES:
            errors.append(f"{sid}: invalid status.")
        if case.get("status") != "PASS":
            errors.append(f"{sid}: not passed.")
        refs = case.get("evidence_refs")
        if not isinstance(refs, list) or not refs or any(
            not isinstance(item, str) or not item.strip() for item in refs
        ):
            errors.append(f"{sid}: missing redacted artifact reference.")
        if sid in {"BC27-03", "BC27-04"} and not isinstance(case.get("scan_id"), str):
            errors.append(f"{sid}: missing real scan ID.")
        if not isinstance(case.get("expected"), str) or not case["expected"].strip():
            errors.append(f"{sid}: missing expected behavior.")
    if record.get("reviewer") is None or not str(record.get("reviewer")).strip():
        errors.append("Missing reviewer.")
    if not isinstance(record.get("decision_utc"), str) or not record["decision_utc"].strip():
        errors.append("Missing UTC decision timestamp.")
    if record.get("decision") != "GO" or record.get("status") != "PASS":
        errors.append("Acceptance must explicitly be reviewed as PASS / GO.")
    raw = json.dumps(record, ensure_ascii=True)
    for pattern in REDACTION_RISKS:
        if pattern.search(raw):
            errors.append("Evidence appears to contain a secret or sensitive field; redact it.")
            break
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True, help="Sanitized evidence JSON; never an API token")
    args = parser.parse_args(argv)
    try:
        evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"NO-GO: could not read evidence: {type(exc).__name__}", file=sys.stderr)
        return 2
    errors = evaluate(evidence)
    if errors:
        for item in errors:
            print(f"NO-GO: {item}", file=sys.stderr)
        return 2
    print("Evidence checklist structurally complete. Manual verification and approval remain required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
