#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_GATES = {
    "PILOT-BC-002",
    "PILOT-BC-003",
    "PILOT-BC-004",
    "PILOT-BC-005",
    "PILOT-BC-006",
    "PILOT-UAT-001",
}
ALLOWED_STATUS = {"PASS", "FAIL", "BLOCKED", "NOT_RUN"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate(data: dict[str, Any], evidence_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "pilot-e2e-01b-v1":
        errors.append("schema_version must be pilot-e2e-01b-v1")

    env = data.get("environment") or {}
    if str(env.get("environment_type", "")).lower() != "sandbox":
        errors.append("environment.environment_type must be sandbox")
    if str(env.get("backend_tier", "")).lower() not in {"dev", "staging"}:
        errors.append("environment.backend_tier must be dev or staging")
    if env.get("backend_ready_http_status") != 200:
        errors.append("environment.backend_ready_http_status must be 200")
    if not UUID_RE.match(str(env.get("company_system_id", ""))):
        errors.append("environment.company_system_id must be a UUID")
    if not SHA_RE.match(str(env.get("app_commit_sha", ""))):
        errors.append("environment.app_commit_sha must be a 40-character lowercase commit SHA")
    for field in ("environment_name", "bc_version", "company_name", "app_version"):
        value = str(env.get(field, "")).strip()
        if not value or value == "REPLACE_ME":
            errors.append(f"environment.{field} must be completed")

    gates = data.get("gates")
    if not isinstance(gates, list):
        errors.append("gates must be a list")
        gates = []
    seen: set[str] = set()
    for gate in gates:
        gate_id = str(gate.get("id", ""))
        if gate_id in seen:
            errors.append(f"duplicate gate id: {gate_id}")
        seen.add(gate_id)
        if gate_id not in REQUIRED_GATES:
            errors.append(f"unknown gate id: {gate_id}")
            continue
        status = str(gate.get("status", ""))
        if status not in ALLOWED_STATUS:
            errors.append(f"{gate_id}: invalid status {status}")
        files = gate.get("evidence_files")
        if not isinstance(files, list):
            errors.append(f"{gate_id}: evidence_files must be a list")
            files = []
        if status == "PASS":
            if not gate.get("executed_at_utc"):
                errors.append(f"{gate_id}: PASS requires executed_at_utc")
            if not files:
                errors.append(f"{gate_id}: PASS requires at least one evidence file")
        for raw_path in files:
            path = Path(str(raw_path))
            if path.is_absolute() or ".." in path.parts:
                errors.append(f"{gate_id}: unsafe evidence path {raw_path}")
                continue
            if evidence_root is not None and not (evidence_root / path).is_file():
                errors.append(f"{gate_id}: evidence file not found: {raw_path}")

    missing = REQUIRED_GATES - seen
    if missing:
        errors.append("missing gates: " + ", ".join(sorted(missing)))

    attestation = data.get("attestation") or {}
    if attestation.get("production_used") is not False:
        errors.append("attestation.production_used must be false")
    if attestation.get("real_customer_data_used") is not False:
        errors.append("attestation.real_customer_data_used must be false")
    if attestation.get("secrets_in_evidence") is not False:
        errors.append("attestation.secrets_in_evidence must be false")
    if not str(attestation.get("completed_by", "")).strip() or attestation.get("completed_by") == "REPLACE_ME":
        errors.append("attestation.completed_by must be completed")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--require-all-pass", action="store_true")
    args = parser.parse_args()

    data = _load(args.evidence)
    errors = validate(data, args.evidence_root)
    statuses = {gate.get("id"): gate.get("status") for gate in data.get("gates", [])}
    if args.require_all_pass:
        open_gates = sorted(gate for gate in REQUIRED_GATES if statuses.get(gate) != "PASS")
        if open_gates:
            errors.append("gates not PASS: " + ", ".join(open_gates))

    if errors:
        print("PILOT-E2E-01B EVIDENCE: FAIL")
        for error in errors:
            print(f"- {error}")
        return 2

    print("PILOT-E2E-01B EVIDENCE: PASS")
    for gate in sorted(REQUIRED_GATES):
        print(f"- {gate}: {statuses[gate]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
