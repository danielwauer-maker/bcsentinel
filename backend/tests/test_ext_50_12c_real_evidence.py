"""Real BC export plus offline replay; never connects to BC or a database."""
import hashlib
import importlib.util
import json
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('real_reconcile', ROOT / 'scripts/reconcile_ext_50_12c.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
RAW = (ROOT / 'quality/release/ext-50-12c-dev-run1-evidence.json').read_bytes()


def evidence():
    return json.loads(RAW.decode('utf-8-sig'), parse_float=Decimal)


def test_real_export_provenance_totals_and_complete_replay():
    assert hashlib.sha256(RAW).hexdigest() == audit.EVIDENCE_SHA256
    result = audit.reconcile_runtime_export(evidence())
    assert result['rows'] == result['distinct_check_ids'] == 95
    assert result['occurrences'] == 224999
    assert Decimal(result['impact_eur']) == Decimal('2202021.49')
    assert Decimal(result['potential_saving_eur']) == Decimal('1541415.04')
    assert result['direct_generated'] == 2000
    assert result['direct_non_owned'] == 53
    assert result['other_unattributed_occurrences'] == 222946
    assert result['unique_affected_records'] is None
    assert (result['score_numerator'], result['score_weight'], result['score']) == (3410, 90, 38)
    assert result['checks'] == 165
    assert result['large'] == 'BLOCKED'
    assert result['gate'] == 'READY_FOR_EXT_50_12C_REPAIR'
    saved = json.loads((ROOT / 'quality/release/ext-50-12c-runtime-reconciled.json').read_text())
    assert {k: v for k, v in saved.items() if k != 'evidence_sha256'} == result


@pytest.mark.parametrize('code,owned,baseline,total', [
    ('CUSTOMERS_MISSING_EMAIL', 600, 1, 601), ('VENDORS_MISSING_PHONE', 200, 8, 208),
    ('ITEMS_WITHOUT_UNIT_PRICE', 600, 30, 630), ('ITEMS_WITHOUT_UNIT_COST', 600, 14, 614)])
def test_real_direct_attribution(code, owned, baseline, total):
    data = evidence()
    obs = data['scenario_observations'][code]
    assert obs['generated_count'] == obs['matching_owned_count'] == owned
    assert obs['non_owned_nonexcluded_matches'] == baseline
    assert obs['missing_owned_records'] == obs['modified_since_generation'] == obs['excluded_matching_owned_count'] == 0
    assert next(r['affected_count'] for r in data['exports']['bc']['rows'] if r['code'] == code) == total


@pytest.mark.parametrize('mutation', ['extra_root', 'extra_row', 'missing_key', 'type', 'row_count',
    'count', 'impact', 'snapshot', 'owned', 'baseline', 'changed', 'score', 'checks', 'saving', 'company'])
def test_real_reconciliation_rejects_schema_or_evidence_drift(mutation):
    data = evidence()
    row = data['exports']['bc']['rows'][0]
    obs = data['scenario_observations']['CUSTOMERS_MISSING_EMAIL']
    if mutation == 'extra_root': data['new_field'] = 'unexpected'
    elif mutation == 'extra_row': row['email'] = 'unexpected'
    elif mutation == 'missing_key': del row['aggregation_note']
    elif mutation == 'type': row['affected_count'] = True
    elif mutation == 'row_count': data['exports']['bc']['rows'].pop()
    elif mutation == 'count': row['affected_count'] += 1
    elif mutation == 'impact': row['impact_eur'] += Decimal('.01')
    elif mutation == 'snapshot': data['run_snapshot']['affected_records'] += 1
    elif mutation == 'owned': obs['matching_owned_count'] -= 1
    elif mutation == 'baseline': obs['non_owned_nonexcluded_matches'] += 1
    elif mutation == 'changed': obs['modified_since_generation'] = 1
    elif mutation == 'score': data['run_snapshot']['module_scores']['CRM'] = 76
    elif mutation == 'checks': data['run_snapshot']['checks_count'] = 168
    elif mutation == 'saving': data['run_snapshot']['potential_saving_eur'] += Decimal('.01')
    else: data['context']['company'] = 'OTHER'
    with pytest.raises(ValueError):
        audit.reconcile_runtime_export(data)


def test_score_source_formula_and_final_counter_correction_are_explicit():
    source = (ROOT / 'bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al').read_text()
    assert 'exit(100 - ((PenaltyTotal * 100) div (PenaltyTotal + 40)));' in source
    assert 'Score := (WeightedScoreTotal + (EnabledWeightTotal div 2)) div EnabledWeightTotal' in source
    assert 'ChecksCount := ScanCheckMgt.GetExpectedChecksCount(Setup);' in source
    result = audit.reconcile_runtime_export(evidence())
    assert list(result['penalties'].values()) == [45, 215, 46, 51, 218, 14, 26, 0, 0, 0]
    assert list(result['module_scores'].values()) == [48, 16, 47, 44, 16, 75, 61, 100, 100, 100]


def test_actual_projection_preserves_this_run_and_same_code_groups():
    rows = evidence()['exports']['bc']['rows']
    assert audit.backend_projection(rows) == rows
    assert audit.dashboard_occurrences(rows) == 224999
    groups = [dict(code='CUSTOMERS_DUPLICATE_EMAIL', affected_count=n) for n in (2, 3)]
    retained = audit.backend_projection(groups)
    assert retained == groups
    assert audit.dashboard_occurrences(retained) == 5
    oracle = audit.impact_oracle()
    definition = oracle.EXPLICIT_ISSUE_IMPACTS[groups[0]['code']]
    full = sum(oracle._calculate_issue_impact_amount(definition, g['affected_count'], 40) for g in groups)
    kept = sum(oracle._calculate_issue_impact_amount(definition, g['affected_count'], 40) for g in retained)
    assert (full, kept) == (180, 180)
    assert audit.backend_projection(list(reversed(groups))) == list(reversed(groups))


def test_authoritative_markdown_contains_all_95_rows():
    report = (ROOT / 'docs/EXT_50_12C_RUNTIME_DETECTION_RECONCILIATION.md').read_text(encoding='utf-8')
    for row in evidence()['exports']['bc']['rows']:
        assert f"| {row['id']} | {row['code']} | {row['module']} | {row['severity']} | {row['affected_count']:,} | {row['impact_eur']:,.2f} |" in report
