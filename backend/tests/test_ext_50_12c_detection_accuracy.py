"""Static contracts and independent numeric oracle; NOT an AL runtime test."""
import importlib.util
import json
import hashlib
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('accuracy_audit', ROOT / 'scripts/audit_ext_50_12c.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
RUNNER = (ROOT / audit.RUNNER).read_text(encoding='utf-8')
PROCEDURES = {name: body for name, _, body in audit.procedures(RUNNER)}


def test_dev_seed_5001_exact_distribution():
    assert audit.reconstruct() == dict(zip(audit.SCENARIOS, (600, 200, 600, 600)))
    assert sum(audit.reconstruct().values()) == 2000


@pytest.mark.parametrize('rate', [1, 5, 10, 20])
def test_full_blocks_and_item_alternation_have_exact_budget(rate):
    assert list(audit.reconstruct(100, 100, 200, rate=rate).values()) == [rate] * 4


def test_boundary_100_belongs_to_first_item_scenario():
    assert audit.reconstruct(0, 0, 99)[audit.SCENARIOS[2]] == 9
    assert audit.reconstruct(0, 0, 100)[audit.SCENARIOS[2]] == 10
    assert audit.reconstruct(0, 0, 200)[audit.SCENARIOS[3]] == 10
    assert audit.reconstruct(seed=1) == audit.reconstruct(seed=5001)


def test_source_oracle_and_mutually_exclusive_scenarios_are_pinned():
    snapshot = json.loads((ROOT / 'quality/release/ext-50-12c-generator-source.json').read_text(encoding='utf-8'))
    assert snapshot['commit'] == '89faeb721ed5488ee97c07a620c5184deba6f2e8'
    for name, evidence in snapshot['files'].items():
        assert hashlib.sha256(evidence['source'].encode()).hexdigest() == evidence['sha256_lf_utf8']
        current = ROOT / 'bc-performance/src' / name
        if current.exists():
            assert current.read_text(encoding='utf-8') == evidence['source']
    policy = snapshot['files']['BCPPolicy.Codeunit.al']['source']
    batch = snapshot['files']['BCPBatch.Codeunit.al']['source']
    assert '((Sequence mod 100) * 37 + (Seed mod 100)) mod 100 < Rate' in policy
    assert '((GenerationRun.Items div 100) mod 2) = 0' in batch
    assert set(re.findall(r"Scenario := '([^']+)'", batch)) == set(audit.SCENARIOS)
    assert 'if Scenario <> \'\' then\n            GenerationRun."Expected Scenarios" += 1;' in batch


@pytest.mark.parametrize('procedure,entity,field,code', [
    ('RunCustomerMasterDataChecks', 'Customer', 'E-Mail', 'CUSTOMERS_MISSING_EMAIL'),
    ('RunVendorMasterDataChecks', 'Vendor', 'Phone No.', 'VENDORS_MISSING_PHONE'),
    ('RunItemMasterDataChecks', 'Item', 'Unit Price', 'ITEMS_WITHOUT_UNIT_PRICE'),
    ('RunItemMasterDataChecks', 'Item', 'Unit Cost', 'ITEMS_WITHOUT_UNIT_COST'),
])
def test_mapping_checks_actual_predicate_and_aggregation(procedure, entity, field, code):
    body = PROCEDURES[procedure]
    value = '0' if entity == 'Item' else "''"
    assert f'({entity}."{field}" = {value}) and not ExceptionMgt.Is{entity}IssueExcluded({entity}, \'{code}\')' in body
    rows, _ = audit.catalog(RUNNER)
    row = next(row for row in rows if row['code'] == code)
    assert f"{row['counter']} += 1;" in body
    assert row['aggregation'] == 'count'
    aggregate = PROCEDURES['AddCountFinding']
    assert aggregate.index('if AffectedCount <= 0') < aggregate.index('InsertFinding(')
    assert 'IssuesCount += 1;' in aggregate


def test_catalog_covers_every_registered_check():
    source = (ROOT / 'bc-extension/app/src/codeunits/DHScanCheckMgt.Codeunit.al').read_text()
    registered = set(re.findall(r"AddCheck\('([^']+)'", source))
    rows, _ = audit.catalog(RUNNER)
    assert len(rows) == len(registered) == 199
    assert {row['code'] for row in rows} == registered


def test_affected_records_are_occurrences_at_both_layers():
    assert 'AffectedRecords += Finding."Affected Count";' in PROCEDURES['RecalculateScoreMetrics']
    dashboard = (ROOT / 'backend/app/routers/analytics.py').read_text()
    assert 'affected_records = sum(_safe_int(issue.affected_count) for issue in issues)' in dashboard


def test_reported_scores_require_module_selection_evidence():
    weights = [15, 20, 15, 10, 15, 5, 10, 5, 3, 2]
    scores = [48, 16, 47, 44, 16, 75, 61, 100, 100, 100]
    actual_weights = list(map(int, re.findall(r'AddWeightedModuleScore\(Setup\."[^"]+", (\d+),', RUNNER)))
    assert actual_weights == weights
    total = sum(w * s for w, s in zip(weights, scores))
    assert total == 4410
    assert (total + 50) // 100 == 44
    assert (sum(w * s for w, s in zip(weights[:7], scores[:7])) + 45) // 90 == 38


@pytest.mark.parametrize('name', ['RunSystemConfigurationChecks', 'RunInventoryValueChecks'])
@pytest.mark.xfail(strict=True, reason='Existing product metadata defect: declared check count exceeds actual checks; no runtime execution claimed')
def test_declared_check_counts_match_executable_catalog(name):
    rows, _ = audit.catalog(RUNNER)
    declared = int(re.search(r'ChecksCount \+= (\d+);', PROCEDURES[name])[1])
    assert declared == sum(row['procedure'] == name for row in rows)


def test_duplicate_marker_is_persisted_for_existing_lookup():
    assert 'SetRange("Group Key"' in PROCEDURES['FindingExists']
    assert 'Finding.BuildGroupKey' in PROCEDURES['BuildGroupKey']
    assert 'GenerateHash' in (ROOT / 'bc-extension/app/src/tables/DHDeepScanFinding.Table.al').read_text()
    assert 'SetFilter(Title' not in PROCEDURES['FindingExists']
    assert 'ValueMarker' in PROCEDURES['InsertFinding'] or 'Marker' in PROCEDURES['InsertFinding']
