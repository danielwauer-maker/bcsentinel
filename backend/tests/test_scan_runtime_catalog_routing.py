"""Static inventory guard for AL check-output routing.

This checks the source contract, NOT runtime completion nor stable record
identity. In grouped AL code a failure can still leave a check unobserved.
"""

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "bc-extension/app/src/codeunits/DHScanCheckMgt.Codeunit.al"
RUNNER = ROOT / "bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al"


def test_all_catalog_checks_have_exactly_one_output_route():
    catalog = CATALOG.read_text(encoding="utf-8-sig")
    runner = RUNNER.read_text(encoding="utf-8-sig")

    declared = re.findall(r"\\bAddCheck\\('([A-Z0-9_]+)'", catalog)
    aggregate = re.findall(
        r"\\bAddCountFinding\\([^;]*?'([A-Z0-9_]+)'\\s*,\\s*'(?:high|medium|low|critical)'",
        runner,
    )
    individual = re.findall(r"\\bRecordCheckStarted\\([^;]*?'([A-Z0-9_]+)'", runner)

    assert len(declared) == len(set(declared)) == 199, "catalog inventory requires explicit versioned review"
    assert len(aggregate) == 193 and len(individual) == 6, "routing inventory changed; review instrumentation"
    routes = Counter(aggregate + individual)
    assert set(routes) == set(declared), (
        f"missing: {sorted(set(declared) - set(routes))}, "
        f"unknown: {sorted(set(routes) - set(declared))}"
    )
    assert all(count == 1 for count in routes.values()), "duplicated or ambiguous check output route"


def test_aggregated_count_findings_do_not_provide_per_record_comparison_identity():
    runner = RUNNER.read_text(encoding="utf-8-sig")
    helper = runner.split("local procedure AddCountFinding", 1)[1].split("local procedure RecordCheckStarted", 1)[0]
    assert "RecordCheckExecution(DeepScanRun.\\\"Entry No.\\\", IssueCode, 'PASS', 0)" in helper
    assert "RecordCheckExecution(DeepScanRun.\\\"Entry No.\\\", IssueCode, 'FINDINGS', 1)" in helper
    assert "AffectedCount" in helper
    assert "Record SystemId" not in helper
