"""Offline reconciler tests use explicitly synthetic rows, never real-runtime claims."""
import copy
import ast
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('runtime_reconcile', ROOT / 'scripts/reconcile_ext_50_12c.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def reported():
    return json.loads((ROOT / 'quality/release/ext-50-12c-runtime-reported.json').read_text(encoding='utf-8'))


def fixture():
    data = reported()
    data['user_reported'].update(finding_rows=2, affected_occurrences=5, impact_eur='10.00')
    rows = [dict(id='1', code='DUPLICATE_TEST', category='CUSTOMER', severity='high', affected_count=2, impact_eur='4.00'),
            dict(id='2', code='DUPLICATE_TEST', category='CUSTOMER', severity='high', affected_count=3, impact_eur='6.00')]
    for layer in ('bc', 'backend'):
        data['exports'][layer] = dict(company=data['context']['company'], scan_id=data['context']['scan_id'],
                                      complete=True, exported_row_count=2, rows=copy.deepcopy(rows))
    return data


def result_checks(data):
    return {c['name']: c['status'] for c in module.reconcile(data)['checks']}


def test_user_report_does_not_become_runtime_pass():
    result = module.reconcile(reported())
    assert result['status'] == 'BLOCKED'
    assert result['readiness'] == 'NOT_READY_FOR_LARGE'
    assert result['inventories'] == {}
    assert result['reported_score_arithmetic'] == dict(numerator=3410, weight=90, score=38)
    checks = result_checks(reported())
    assert checks['reported_potential_saving_display'] == 'PASS'
    assert checks['bc_inventory'] == checks['backend_inventory'] == 'BLOCKED'


def test_duplicate_codes_are_preserved_as_separate_findings():
    result = module.reconcile(fixture())
    assert result['inventories']['bc']['by_code']['DUPLICATE_TEST'] == dict(rows=2, occurrences=5, impact_eur='10.00')
    assert result_checks(fixture())['bc_backend_finding_multiset'] == 'PASS'


def test_first_row_overwrite_is_not_hidden_by_same_code_join():
    data = fixture()
    data['exports']['bc']['rows'][0]['impact_eur'] = '6.00'
    data['exports']['bc']['rows'][1]['impact_eur'] = '0.00'
    checks = result_checks(data)
    assert checks['bc_backend_finding_multiset'] == 'FAIL'
    assert checks['bc_impact_sum'] == 'FAIL'


@pytest.mark.parametrize('change', ['company', 'scan', 'partial', 'duplicate_id', 'negative_count', 'bool_count', 'nan', 'subcent'])
def test_rejects_invalid_or_mismatched_exports(change):
    data = fixture()
    export = data['exports']['bc']
    if change == 'company': export['company'] = 'OTHER'
    elif change == 'scan': export['scan_id'] = 'OTHER'
    elif change == 'partial': export['complete'] = False
    elif change == 'duplicate_id': export['rows'][1]['id'] = '1'
    elif change == 'negative_count': export['rows'][0]['affected_count'] = -1
    elif change == 'bool_count': export['rows'][0]['affected_count'] = True
    elif change == 'nan': export['rows'][0]['impact_eur'] = 'NaN'
    else: export['rows'][0]['impact_eur'] = '0.001'
    with pytest.raises(ValueError): module.reconcile(data)


def test_baseline_does_not_mask_missing_generated_fields():
    data = reported()
    rows, observations = [], {}
    for index, (code, count) in enumerate(module.EXPECTED.items()):
        rows.append(dict(id=str(index), code=code, category='ITEM', severity='medium', affected_count=count, impact_eur='0.00'))
        observations[code] = dict(generated_count=count, matching_owned_count=0,
                                  excluded_matching_owned_count=0, non_owned_nonexcluded_matches=count)
    data['exports']['bc'] = dict(company=data['context']['company'], scan_id=data['context']['scan_id'],
                                complete=True, exported_row_count=4, rows=rows)
    data['scenario_observations'] = observations
    checks = result_checks(data)
    for code in module.EXPECTED:
        assert checks[code + '_injection_fields'] == 'FAIL'
        assert checks[code + '_detection'] == 'PASS'
    assert module.reconcile(data)['status'] == 'FAIL'


def test_165_is_catalog_count_for_seven_reported_modules():
    catalog = json.loads((ROOT / 'quality/release/ext-50-12c-static-audit.json').read_text(encoding='utf-8'))
    enabled = [c for c in catalog['checks'] if c['category'] not in ('SERVICE', 'JOB', 'HR')]
    assert len(enabled) == 165
    # Excludes the 34 registered checks of the three inactive modules; not 168 hardcoded runner increments.
    assert 199 - 12 - 10 - 12 == 165


def test_actual_sync_source_discards_earlier_same_code_rows():
    source = ast.parse((ROOT / 'backend/app/routers/scans.py').read_text(encoding='utf-8'))
    function = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'sync_scan')
    assignment = next(n for n in ast.walk(function) if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == 'recalculated_issues' for t in n.targets))
    first = dict(code='DUPLICATE_TEST', affected_count=2, estimated_impact_eur=4)
    last = dict(code='DUPLICATE_TEST', affected_count=3, estimated_impact_eur=6)
    actual = eval(compile(ast.Expression(assignment.value), '<actual sync projection>', 'eval'),
                  {'commercials': {'issues': [first, last]}})
    assert actual == [last]
    assert sum(row['affected_count'] for row in actual) == 3  # Not 5.


def test_last_per_code_export_is_distinguished_from_lossless_reconciliation():
    data = fixture()
    data['exports']['backend']['rows'] = [data['exports']['backend']['rows'][1]]
    data['exports']['backend']['exported_row_count'] = 1
    checks = result_checks(data)
    assert checks['backend_matches_current_last_per_code_behavior'] == 'PASS'
    assert checks['bc_backend_finding_multiset'] == 'FAIL'


def test_diagnostic_download_is_consumed_without_overwriting_original(tmp_path):
    data = fixture()
    exported = dict(evidence_kind='BC_PERSISTED_FINDINGS_AND_CURRENT_READ_ONLY_ATTRIBUTION',
                    context=data['context'], exports={'bc': data['exports']['bc']},
                    scenario_observations={code: dict(generated_count=n, matching_owned_count=n,
                        excluded_matching_owned_count=0, non_owned_nonexcluded_matches=0)
                        for code, n in module.EXPECTED.items()},
                    run_snapshot=dict(score=38, module_scores=data['user_reported']['module_scores'], estimated_loss_eur='10.00'))
    input_path, export_path, output_path = (tmp_path / name for name in ('reported.json', 'bc.json', 'result.json'))
    input_path.write_text(json.dumps(data), encoding='utf-8')
    export_path.write_text(json.dumps(exported), encoding='utf-8-sig')
    original = export_path.read_bytes()
    run = subprocess.run([sys.executable, str(ROOT / 'scripts/reconcile_ext_50_12c.py'),
                          '--input', str(input_path), '--bc-export', str(export_path),
                          '--output', str(output_path)], capture_output=True, text=True)
    assert run.returncode == 1  # Synthetic rows intentionally do not match four scenario counts.
    result = json.loads(output_path.read_text())
    assert result['inventories']['bc']['row_count'] == 2
    assert len(result['bc_export_sha256']) == 64
    assert export_path.read_bytes() == original
