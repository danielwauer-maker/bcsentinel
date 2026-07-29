#!/usr/bin/env python3
"""Generate deterministic PILOT-E2E readiness evidence.

The generator never upgrades BLOCKED or MANUAL gates to PASS. Automated entries
are PASS only when matching repository tests/contracts exist and the supplied
JUnit suite completed without failures or errors.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX = ROOT / "quality" / "pilot-e2e" / "pilot_test_matrix.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _matching_paths(patterns: list[str]) -> list[str]:
    matches: set[str] = set()
    for pattern in patterns:
        for match in glob.glob(str(ROOT / pattern), recursive=True):
            path = Path(match)
            if path.is_file():
                matches.add(path.relative_to(ROOT).as_posix())
    return sorted(matches)


def _read_junit(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {
            "available": False,
            "tests": 0,
            "failures": 0,
            "errors": 0,
            "skipped": 0,
            "time_seconds": 0.0,
        }

    root = ElementTree.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    totals = Counter()
    elapsed = 0.0
    for suite in suites:
        for key in ("tests", "failures", "errors", "skipped"):
            totals[key] += int(suite.attrib.get(key, "0"))
        elapsed += float(suite.attrib.get("time", "0") or 0)
    return {
        "available": True,
        "tests": totals["tests"],
        "failures": totals["failures"],
        "errors": totals["errors"],
        "skipped": totals["skipped"],
        "time_seconds": round(elapsed, 3),
    }


def _status_for(test: dict[str, Any], matched: list[str], junit: dict[str, Any]) -> tuple[str, str]:
    execution = test["execution"]
    if execution == "automated":
        if not matched:
            return "FAIL", "No matching automated test or contract was found."
        if not junit["available"]:
            return "NOT_RUN", "Matching coverage exists, but no JUnit result was supplied."
        if junit["failures"] or junit["errors"]:
            return "FAIL", "The automated regression suite reported failures or errors."
        return "PASS", "Matching coverage exists and the supplied regression suite passed."
    if execution == "automated_external":
        return "BLOCKED", "Requires its dedicated external CI workflow evidence."
    if execution in {"environment_required", "manual_or_sandbox_automation"}:
        return "BLOCKED", test.get("blocker", "Required execution environment is unavailable.")
    if execution == "manual":
        return "MANUAL", "Human acceptance evidence is required."
    return "NOT_RUN", f"Unknown execution mode: {execution}"


def build_report(matrix: dict[str, Any], junit: dict[str, Any]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for test in matrix["tests"]:
        matched = _matching_paths(test.get("source_patterns", []))
        status, reason = _status_for(test, matched, junit)
        entries.append(
            {
                **test,
                "status": status,
                "status_reason": reason,
                "matched_sources": matched,
            }
        )

    counts = Counter(entry["status"] for entry in entries)
    p0 = [entry for entry in entries if entry["priority"] == "P0"]
    automated_p0 = [entry for entry in p0 if entry["execution"] == "automated"]
    automated_p0_ready = bool(automated_p0) and all(entry["status"] == "PASS" for entry in automated_p0)
    open_p0 = [entry["id"] for entry in p0 if entry["status"] != "PASS"]

    return {
        "schema_version": matrix["schema_version"],
        "generated_at_utc": _utc_now(),
        "repository": os.getenv("GITHUB_REPOSITORY", "local"),
        "git_ref": os.getenv("GITHUB_REF_NAME", "local"),
        "git_sha": os.getenv("GITHUB_SHA", "unknown"),
        "junit": junit,
        "summary": {
            "total": len(entries),
            "status_counts": dict(sorted(counts.items())),
            "p0_total": len(p0),
            "p0_automated_total": len(automated_p0),
            "p0_automated_ready": automated_p0_ready,
            "open_p0": open_p0,
            "overall_decision": "NOT_READY" if open_p0 else "READY",
        },
        "tests": entries,
    }


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    counts = summary["status_counts"]
    lines = [
        "# PILOT-E2E-01A Evidence Report",
        "",
        f"Generated: `{report['generated_at_utc']}`  ",
        f"Commit: `{report['git_sha']}`  ",
        f"Ref: `{report['git_ref']}`",
        "",
        "## Decision",
        "",
        f"**{summary['overall_decision']}**",
        "",
        "The automated foundation is not a substitute for a real Business Central sandbox run. "
        "BLOCKED and MANUAL gates remain open until separate evidence is attached.",
        "",
        "## Summary",
        "",
        f"- Total gates: {summary['total']}",
        f"- P0 gates: {summary['p0_total']}",
        f"- Automated P0 gates mapped: {summary['p0_automated_total']}",
        f"- Automated P0 foundation ready: {'YES' if summary['p0_automated_ready'] else 'NO'}",
        f"- PASS: {counts.get('PASS', 0)}",
        f"- FAIL: {counts.get('FAIL', 0)}",
        f"- BLOCKED: {counts.get('BLOCKED', 0)}",
        f"- MANUAL: {counts.get('MANUAL', 0)}",
        f"- NOT_RUN: {counts.get('NOT_RUN', 0)}",
        "",
        "## JUnit regression",
        "",
        f"- Available: {report['junit']['available']}",
        f"- Tests: {report['junit']['tests']}",
        f"- Failures: {report['junit']['failures']}",
        f"- Errors: {report['junit']['errors']}",
        f"- Skipped: {report['junit']['skipped']}",
        "",
        "## Gate results",
        "",
        "| ID | Priority | Area | Status | Coverage/Evidence |",
        "|---|---|---|---|---|",
    ]
    for entry in report["tests"]:
        sources = ", ".join(entry["matched_sources"][:3])
        if len(entry["matched_sources"]) > 3:
            sources += f" (+{len(entry['matched_sources']) - 3})"
        evidence = sources or entry["status_reason"]
        evidence = evidence.replace("|", "\\|")
        lines.append(
            f"| {entry['id']} | {entry['priority']} | {entry['area']} | "
            f"**{entry['status']}** | {evidence} |"
        )
    lines.extend(
        [
            "",
            "## Open P0 gates",
            "",
        ]
    )
    if summary["open_p0"]:
        lines.extend(f"- `{test_id}`" for test_id in summary["open_p0"])
    else:
        lines.append("None.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--junit", type=Path)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    parser.add_argument(
        "--fail-on-automated-p0",
        action="store_true",
        help="Return non-zero when an automated P0 gate is not PASS.",
    )
    args = parser.parse_args()

    matrix = _load_json(args.matrix)
    junit = _read_junit(args.junit)
    report = build_report(matrix, junit)

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.markdown_out.write_text(_markdown(report), encoding="utf-8")

    print(json.dumps(report["summary"], indent=2))
    if args.fail_on_automated_p0 and not report["summary"]["p0_automated_ready"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
