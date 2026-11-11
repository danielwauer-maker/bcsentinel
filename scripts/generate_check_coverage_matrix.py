#!/usr/bin/env python3
"""Generate the Sprint 3B.01 check-lifecycle inventory from AL source.

The committed CSV is deliberately derived from the current catalog and runner
instead of a hand-maintained historical check list.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "bc-extension/app/src/codeunits/DHScanCheckMgt.Codeunit.al"
RUNNER = ROOT / "bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al"
OUTPUT = ROOT / "docs/checks/sprint3b01-check-coverage.csv"


def procedure_bodies(source: str) -> dict[str, str]:
    return {
        name: body
        for name, body in re.findall(
            r"^    local procedure (Run\w+?)\([^\n]+\)(.*?)(?=^    (?:local )?procedure |\Z)",
            source,
            re.MULTILINE | re.DOTALL,
        )
    }


def main() -> None:
    catalog = CATALOG.read_text(encoding="utf-8-sig")
    runner = RUNNER.read_text(encoding="utf-8-sig")
    declared = re.findall(r"\bAddCheck\('([A-Z0-9_]+)', '([A-Z]+)'", catalog)
    if len(declared) != 199 or len({code for code, _ in declared}) != 199:
        raise SystemExit("Expected exactly 199 unique catalog checks.")

    bodies = procedure_bodies(runner)
    aggregate_routes: dict[str, str] = {}
    for procedure, body in bodies.items():
        for code in re.findall(
            r"\bAddCountFinding\([^;]*?'([A-Z0-9_]+)'\s*,\s*'(?:high|medium|low|critical)'",
            body,
        ):
            if code in aggregate_routes:
                raise SystemExit(f"Aggregate route is ambiguous for {code}.")
            aggregate_routes[code] = procedure

    duplicate_routes = {
        code: procedure
        for procedure, body in bodies.items()
        for code in re.findall(r"\bRecordCheckStarted\([^;]*?'([A-Z0-9_]+)'", body)
    }
    routes = set(aggregate_routes) | set(duplicate_routes)
    declared_codes = {code for code, _ in declared}
    if routes != declared_codes or set(aggregate_routes) & set(duplicate_routes):
        raise SystemExit("Catalog and execution routes do not form an exact one-to-one inventory.")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=(
            "check_code", "bc_module", "execution_route", "check_type",
            "started_capture", "terminal_status", "error_exception_handling",
            "backend_evidence", "test_coverage", "runtime_evidence",
        ))
        writer.writeheader()
        for code, module in declared:
            if code in aggregate_routes:
                route = aggregate_routes[code]
                check_type = "aggregate-count"
                started = "RecordCountChecksStarted before aggregate traversal"
                terminal = "AddCountFinding: PASS/FINDINGS; disabled: SKIPPED"
            else:
                route = duplicate_routes[code]
                check_type = "duplicate-group"
                started = "RecordCheckStarted before individual query"
                terminal = "RecordCompletedCheck: PASS/FINDINGS; disabled: SKIPPED"
            writer.writerow({
                "check_code": code,
                "bc_module": module,
                "execution_route": route,
                "check_type": check_type,
                "started_capture": started,
                "terminal_status": terminal,
                "error_exception_handling": (
                    "outer TryFunction -> MarkRunAsFailed; started checks -> FAILED; "
                    "proven unreached checks -> NOT_EXECUTED; unknown remains unobserved"
                ),
                "backend_evidence": (
                    "success: bc-check-execution-partial-v1; "
                    "failure: bc-check-failure-partial-v1; immutable leased retry"
                ),
                "test_coverage": "backend/tests/test_sprint3b01_check_coverage.py",
                "runtime_evidence": "OPEN: real BC27 sandbox lifecycle evidence required",
            })


if __name__ == "__main__":
    main()
