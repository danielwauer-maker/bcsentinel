"""Sprint 3B.01 static coverage matrix and aggregate lifecycle contract."""

import csv
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al"
MATRIX = ROOT / "docs/checks/sprint3b01-check-coverage.csv"
GENERATOR = ROOT / "scripts/generate_check_coverage_matrix.py"


def test_coverage_matrix_is_current_complete_and_machine_readable():
    before = MATRIX.read_bytes() if MATRIX.exists() else None
    subprocess.run([sys.executable, str(GENERATOR)], cwd=ROOT, check=True)
    assert MATRIX.read_bytes() == before, "Run scripts/generate_check_coverage_matrix.py and commit the matrix."
    with MATRIX.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 199
    assert len({row["check_code"] for row in rows}) == 199
    assert Counter(row["check_type"] for row in rows) == {
        "aggregate-count": 193,
        "duplicate-group": 6,
    }
    assert {row["runtime_evidence"] for row in rows} == {
        "OPEN: real BC27 sandbox lifecycle evidence required"
    }


def test_all_aggregate_routes_persist_started_before_their_traversal():
    runner = RUNNER.read_text(encoding="utf-8-sig")
    assert "local procedure RecordCountChecksStarted" in runner
    assert "local procedure RecordCountCheckStarted" in runner
    assert "RecordCheckStarted(DeepScanRun.\"Entry No.\", IssueCode);" in runner

    with MATRIX.open(encoding="utf-8", newline="") as handle:
        aggregate_codes = {
            row["check_code"] for row in csv.DictReader(handle)
            if row["check_type"] == "aggregate-count"
        }
    declared_by_group = set()
    for calls in re.findall(
        r"RecordCountChecksStarted\(DeepScanRun, '([^']+)'\);", runner
    ):
        declared_by_group.update(calls.split("|"))
    assert declared_by_group == aggregate_codes


def test_aggregate_started_boundaries_precede_their_counting_work():
    runner = RUNNER.read_text(encoding="utf-8-sig")
    with MATRIX.open(encoding="utf-8", newline="") as handle:
        routes = {
            row["execution_route"] for row in csv.DictReader(handle)
            if row["check_type"] == "aggregate-count"
        }
    for route in routes:
        body = runner.split(f"local procedure {route}", 1)[1].split("local procedure ", 1)[0]
        assert "RecordCountChecksStarted(DeepScanRun," in body
        assert body.index("RecordCountChecksStarted(DeepScanRun,") < body.index("ChecksCount +=")
