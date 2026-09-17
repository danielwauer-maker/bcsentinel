"""Offline reconciliation of sanitized exports. No network, SQL, BC writes or credentials."""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import re
import sys
import types
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

WEIGHTS = dict(zip(('System', 'Finance', 'Sales', 'Purchasing', 'Inventory', 'CRM',
                    'Manufacturing', 'Service', 'Jobs', 'HR'), (15, 20, 15, 10, 15, 5, 10, 5, 3, 2)))
EXPECTED = dict(zip(('CUSTOMERS_MISSING_EMAIL', 'VENDORS_MISSING_PHONE',
                     'ITEMS_WITHOUT_UNIT_PRICE', 'ITEMS_WITHOUT_UNIT_COST'), (600, 200, 600, 600)))
EVIDENCE_SHA256 = '4914706b1f8d259a0c46e4002a7dda20ac347be08b5bee5c46226504e4ba179f'
ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_shape(value, schema, path='$'):
    """Closed export schema: unexpected fields and nested type changes are errors."""
    if isinstance(schema, dict):
        require(isinstance(value, dict) and set(value) == set(schema), 'Schema keys: ' + path)
        for key, child in schema.items():
            validate_shape(value[key], child, path + '.' + key)
    elif isinstance(schema, list):
        require(isinstance(value, list), 'Schema array: ' + path)
        for child in value:
            validate_shape(child, schema[0], path + '[]')
    else:
        valid = {'string': isinstance(value, str), 'boolean': type(value) is bool,
                 'number': type(value) in (int, float, Decimal)}[schema]
        require(valid, 'Schema type: ' + path)


def impact_oracle(root=ROOT):
    """Execute only existing pure pricing functions/constants; no app/DB imports."""
    path = root / 'backend/app/services/impact_service.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    names = {'_normalize_code', '_infer_category', '_round_money', '_fallback_definition',
             '_calculate_issue_impact_amount', 'clamp_potential_saving_factor',
             'normalize_commercial_values'}
    nodes = [n for n in tree.body if
             (isinstance(n, ast.ImportFrom) and n.module in ('__future__', 'dataclasses')) or
             (isinstance(n, ast.ClassDef) and n.name == 'ImpactDefinition') or
             (isinstance(n, ast.FunctionDef) and n.name in names) or
             (isinstance(n, ast.Assign) and all(isinstance(t, ast.Name) and t.id.startswith('DEFAULT_') for t in n.targets)) or
             (isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id == 'EXPLICIT_ISSUE_IMPACTS')]
    module = types.ModuleType('_ext_50_12c_pure_impact')
    sys.modules[module.__name__] = module
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), module.__dict__)
    return module


def source_assignment(root, path, function, target, scope):
    tree = ast.parse((root / path).read_text(encoding='utf-8'))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
    node = next(n for n in ast.walk(fn) if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == target for t in n.targets))
    return eval(compile(ast.Expression(node.value), str(path), 'eval'), scope)


def backend_projection(rows, root=ROOT):
    return source_assignment(root, 'backend/app/routers/scans.py', 'sync_scan',
                             'recalculated_issues', {'commercials': {'issues': rows}})


def dashboard_occurrences(rows, root=ROOT):
    return source_assignment(root, 'backend/app/routers/analytics.py', '_build_dashboard_payload',
                             'affected_records', {'issues': [types.SimpleNamespace(**r) for r in rows], '_safe_int': int})


def reconcile_runtime_export(data, root=ROOT):
    """Authoritative single-run audit; raises on any inconsistent runtime invariant.

    Source-derived score/impact replay proves numerical consistency, not the identity
    of an unavailable deployed backend/configuration snapshot.
    """
    schema = json.loads((root / 'quality/release/ext-50-12c-export-schema.json').read_text())
    validate_shape(data, schema)
    require(data['schema_version'] == 1 and data['evidence_kind'] == 'BC_PERSISTED_FINDINGS_AND_CURRENT_READ_ONLY_ATTRIBUTION', 'Export version/kind')
    context, snapshot, export = data['context'], data['run_snapshot'], data['exports']['bc']
    scan = 'RUN_20260916_000001_43F57A071BFF485BAF20C68FF578B'
    require(context['company'] == export['company'] == 'BCS-PERF-DEV' and context['scan_id'] == export['scan_id'] == scan, 'Run identity')
    require(integer(context['generator_run_id']) == 1 and context['bcsentinel_version'] == '1.0.2.21' and context['generator_version'] == '1.0.0.1', 'Versions/generator')
    rows = export['rows']
    require(export['complete'] is True and integer(export['exported_row_count']) == len(rows) == integer(snapshot['issues_count']) == 95, '95 complete finding rows required')
    require(len({r['id'] for r in rows}) == len(rows) and all(r['id'].isdigit() for r in rows), 'Unique numeric entry IDs')
    require([int(r['id']) for r in rows] == sorted(int(r['id']) for r in rows), 'Payload order')
    spec = importlib.util.spec_from_file_location('_ext_50_12c_catalog', root / 'scripts/audit_ext_50_12c.py')
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    source = (root / audit.RUNNER).read_text(encoding='utf-8')
    catalog = {r['code']: r for r in audit.catalog(source)[0]}
    procedures = {name: body for name, _, body in audit.procedures(source)}
    critical_markers = re.findall(r"StrPos\(IssueCodeUpper, '([^']+)'\)", procedures['IsCriticalImpactIssue'])
    penalties = dict.fromkeys(WEIGHTS, 0)
    totals = {m: dict(rows=0, occurrences=0, impact_eur=Decimal(0)) for m in WEIGHTS}
    oracle, inventory = impact_oracle(root), []
    category_module = dict(SYSTEM='System', FINANCE='Finance', CUSTOMER='Finance', VENDOR='Finance', LEDGER='Finance',
                           SALES='Sales', PURCHASE='Purchasing', INVENTORY='Inventory', ITEM='Inventory', CRM='CRM',
                           MANUFACTURING='Manufacturing', SERVICE='Service', JOB='Jobs', HR='HR')
    for row in rows:
        code, count, amount = row['code'], integer(row['affected_count']), money(row['impact_eur'])
        require(code in catalog and row['check_name'] == code and row['scan_id'] == scan, 'Finding identity/catalog')
        entry = catalog[code]
        require(row['category'] == entry['category'] and row['module'] == category_module[entry['category']], 'Finding module')
        require(row['severity'] in ('low', 'medium', 'high', 'critical'), 'Finding severity')
        require(entry['aggregation'] == 'count' and row['aggregation_key_available'] is False, 'Unexpected group finding in this run')
        severity = entry['severity']
        if severity == 'high' and (any(marker in code for marker in critical_markers) or
                                  (entry['initial_penalty'] >= 7 and count >= 10) or count >= 1000):
            severity = 'critical'
        require(row['severity'] == severity, 'Exported/pre-sync severity differs: ' + code)
        tier = next((p for threshold, p in ((5000, 8), (1000, 6), (250, 4), (50, 2), (1, 1)) if count >= threshold), 0)
        penalties[row['module']] += {'low': 1, 'medium': 3, 'high': 6, 'critical': 10}[severity] + tier
        definition = oracle.EXPLICIT_ISSUE_IMPACTS.get(code) or oracle._fallback_definition(code)
        expected_impact = money(oracle._calculate_issue_impact_amount(definition, count, oracle.DEFAULT_HOURLY_RATE_EUR))
        require(amount == expected_impact, 'Default impact replay mismatch: ' + code)
        total = totals[row['module']]
        total['rows'] += 1
        total['occurrences'] += count
        total['impact_eur'] += amount
        observation = data['scenario_observations'].get(code)
        inventory.append(dict(entry_no=row['id'], code=code, module=row['module'], severity=row['severity'],
                              pre_sync_source_severity=severity, affected_count=count, impact_eur=str(amount),
                              generated_matches=observation['matching_owned_count'] if observation else None,
                              non_owned_matches=observation['non_owned_nonexcluded_matches'] if observation else None,
                              cronus_origin='UNPROVEN', aggregation='One company-wide count per check; overlaps across checks',
                              verdict='DIRECT_DETECTION_RECONCILED' if observation else 'ARITHMETIC_RECONCILED_MEMBERSHIP_UNPROVEN',
                              suspected_row_defect=None, evidence_level='BC_RUNTIME_PLUS_UNCHANGED_OWNED_FIELDS' if observation else 'BC_RUNTIME_AGGREGATE_PLUS_SOURCE',
                              predicate=entry['condition'], procedure=entry['procedure'],
                              impact_parameters=dict(minutes=definition.minutes_per_occurrence, probability=definition.probability,
                                                     frequency=definition.frequency_per_year, hourly_rate=40)))
    occurrences = sum(r['affected_count'] for r in rows)
    impact = sum((money(r['impact_eur']) for r in rows), Decimal(0))
    require(occurrences == integer(snapshot['affected_records']) == integer(snapshot['exported_occurrences']) == 224999, 'Occurrence totals')
    require(impact == money(snapshot['estimated_loss_eur']) == money(snapshot['exported_row_impact_eur']) == Decimal('2202021.49'), 'Impact totals')
    require(set(data['scenario_observations']) == set(EXPECTED), 'Four direct scenarios')
    for code, expected, baseline in zip(EXPECTED, EXPECTED.values(), (1, 8, 30, 14)):
        obs = data['scenario_observations'][code]
        require(all(integer(obs[k]) == v for k, v in dict(generated_count=expected, matching_owned_count=expected,
                    excluded_matching_owned_count=0, non_owned_nonexcluded_matches=baseline, missing_owned_records=0,
                    modified_since_generation=0).items()), 'Direct attribution mismatch: ' + code)
        matches = [r for r in rows if r['code'] == code]
        require(len(matches) == 1 and matches[0]['affected_count'] == expected + baseline, 'Direct finding mismatch: ' + code)
    enabled = [m for m, flag in data['current_setup_not_scan_time_snapshot'].items() if flag]
    require(enabled == list(WEIGHTS)[:7], 'Seven expected active modules')
    module_scores = {m: 100 - 100 * p // (p + 40) for m, p in penalties.items()}
    require(module_scores == snapshot['module_scores'], 'Finding-derived module scores')
    numerator = sum(module_scores[m] * WEIGHTS[m] for m in enabled)
    denominator = sum(WEIGHTS[m] for m in enabled)
    score = (numerator + denominator // 2) // denominator
    require(score == integer(snapshot['score']) == 38, 'Overall score')
    checks = sum(category_module[c['category']] in enabled for c in catalog.values())
    require(checks == integer(snapshot['checks_count']) == 165, 'Enabled check catalog')
    require('ChecksCount := ScanCheckMgt.GetExpectedChecksCount(Setup);' in procedures['RunChecks'], 'Final counter normalization missing')
    saving = money(oracle.normalize_commercial_values(estimated_loss_eur=float(impact), estimated_premium_price_monthly=0)['potential_saving_eur'])
    require(saving == money(snapshot['potential_saving_eur']) == Decimal('1541415.04'), 'Saving replay')
    retained = backend_projection(rows, root)
    require(len(retained) == len(rows) == 95, 'Unexpected duplicate Check-ID in this run')
    require(dashboard_occurrences(retained, root) == occurrences, 'Dashboard projection occurrences')
    for total in totals.values():
        total['impact_eur'] = str(total['impact_eur'])
    return dict(status='PASS', gate='READY_FOR_EXT_50_12C_REPAIR', large='BLOCKED',
                evidence_kind='REAL_BC_SAAS_EXPORT_WITH_OFFLINE_SOURCE_REPLAY',
                backend_persisted_export='NOT_SUPPLIED; projection only, no live backend identity assertion',
                rows=95, distinct_check_ids=len(retained), occurrences=occurrences, impact_eur=str(impact),
                potential_saving_eur=str(saving), direct_generated=2000, direct_non_owned=53,
                other_unattributed_occurrences=occurrences-2053, unique_affected_records=None,
                penalties=penalties, module_scores=module_scores, score=score, score_numerator=numerator,
                score_weight=denominator, checks=checks, module_totals=totals, inventory=inventory)


def integer(value):
    if type(value) is not int or value < 0:
        raise ValueError('Expected a nonnegative integer')
    return value


def money(value):
    if isinstance(value, bool):
        raise ValueError('Invalid money')
    result = Decimal(str(value))
    if not result.is_finite() or result < 0 or result != result.quantize(Decimal('.01')):
        raise ValueError('Money must be finite, nonnegative and have at most two decimals')
    return result


def reconcile(data):
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported schema')
    context = data['context']
    if context['company'] != 'BCS-PERF-DEV' or context['scan_id'] != 'RUN_20260916_000001_43F57A071BFF485BAF20C68FF578B':
        raise ValueError('This contract is scoped to the preserved DEV run')
    reported = data['user_reported']
    checks, inventories = [], {}

    def check(name, condition=None, detail=''):
        checks.append(dict(name=name, status='BLOCKED' if condition is None else ('PASS' if condition else 'FAIL'), detail=detail))

    modules = reported['enabled_modules']
    if len(modules) != len(set(modules)) or not modules or any(m not in WEIGHTS for m in modules):
        raise ValueError('Invalid module selection')
    scores = reported['module_scores']
    if set(scores) != set(WEIGHTS) or any(integer(v) > 100 for v in scores.values()):
        raise ValueError('Expected all ten bounded module scores')
    numerator = sum(WEIGHTS[m] * scores[m] for m in modules)
    denominator = sum(WEIGHTS[m] for m in modules)
    computed_score = (numerator + denominator // 2) // denominator
    check('reported_score_consistency', computed_score == integer(reported['score']),
          'Arithmetic on user-reported values; not a finding-derived runtime score')
    check('reported_potential_saving_display',
          int((money(reported['impact_eur']) * Decimal('.7')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)) == integer(reported['potential_saving_display_eur']),
          'Conditional on the default 0.7 factor; runtime configuration not supplied')

    exports = data.get('exports', {})
    snapshot = data.get('run_snapshot')
    if snapshot is not None:
        check('bc_saved_score', integer(snapshot['score']) == integer(reported['score']))
        check('bc_saved_module_scores', snapshot['module_scores'] == scores)
        check('bc_saved_total_impact', money(snapshot['estimated_loss_eur']) == money(reported['impact_eur']))
    for layer in ('bc', 'backend'):
        export = exports.get(layer)
        if export is None:
            check(layer + '_inventory', detail='No complete sanitized export supplied')
            continue
        if export.get('company') != context['company'] or export.get('scan_id') != context['scan_id']:
            raise ValueError('Export belongs to a different company or scan')
        rows = export['rows']
        if export.get('complete') is not True or integer(export['exported_row_count']) != len(rows):
            raise ValueError('Partial or inconsistent export')
        seen, grouped = set(), defaultdict(list)
        for row in rows:
            identity = row['id']
            if not isinstance(identity, str) or not identity or identity in seen:
                raise ValueError('Finding IDs must be nonempty and unique within each export')
            seen.add(identity)
            if not isinstance(row['code'], str) or not row['code'] or not isinstance(row['category'], str):
                raise ValueError('Invalid check code/category')
            if row['severity'] not in ('low', 'medium', 'high', 'critical'):
                raise ValueError('Invalid severity')
            count, impact = integer(row['affected_count']), money(row['impact_eur'])
            grouped[row['code']].append((count, impact))
        occurrences = sum(integer(r['affected_count']) for r in rows)
        impact_sum = sum((money(r['impact_eur']) for r in rows), Decimal(0))
        inventories[layer] = {'row_count': len(rows), 'distinct_check_codes': len(grouped),
                              'occurrences': occurrences, 'impact_eur': str(impact_sum),
                              'by_code': {code: {'rows': len(values), 'occurrences': sum(v[0] for v in values),
                                                'impact_eur': str(sum((v[1] for v in values), Decimal(0)))}
                                          for code, values in sorted(grouped.items())}}
        check(layer + '_row_count', len(rows) == integer(reported['finding_rows']))
        check(layer + '_occurrences', occurrences == integer(reported['affected_occurrences']))
        check(layer + '_impact_sum', impact_sum == money(reported['impact_eur']),
              'BC row impacts may expose same-code response matching; do not silently replace with backend amounts')

    if len(inventories) == 2:
        def values(layer):
            return Counter((r['code'], integer(r['affected_count']), money(r['impact_eur'])) for r in exports[layer]['rows'])
        check('bc_backend_finding_multiset', values('bc') == values('backend'),
              'Preserves multiple groups per code; never joins only the first occurrence')
        last_by_code = {r['code']: r for r in exports['bc']['rows']}
        expected_last = Counter((r['code'], integer(r['affected_count'])) for r in last_by_code.values())
        actual_backend = Counter((r['code'], integer(r['affected_count'])) for r in exports['backend']['rows'])
        check('backend_matches_current_last_per_code_behavior', expected_last == actual_backend,
              'Source behavior, not approval of data loss; BC rows must retain original payload order')
    else:
        check('bc_backend_finding_multiset', detail='Both complete exports required')

    observations = data.get('scenario_observations')
    if observations is None or 'bc' not in inventories:
        check('generator_runtime_detection', detail='Owned field counts, exceptions, baseline matches and BC findings required')
    else:
        if set(observations) != set(EXPECTED):
            raise ValueError('All four scenario observations are required')
        for code, expected in EXPECTED.items():
            o = observations[code]
            generated = integer(o['generated_count'])
            matches = integer(o['matching_owned_count'])
            excluded = integer(o['excluded_matching_owned_count'])
            baseline = integer(o['non_owned_nonexcluded_matches'])
            if excluded > matches or matches > generated:
                raise ValueError('Invalid owned/excluded counts')
            row = inventories['bc']['by_code'].get(code)
            check(code + '_injection_fields', generated == expected and matches == expected)
            if 'modified_since_generation' in o and 'missing_owned_records' in o:
                check(code + '_unchanged_since_generation',
                      integer(o['modified_since_generation']) == 0 and integer(o['missing_owned_records']) == 0,
                      'Current-state attribution must not silently stand in for changed historical data')
            total = baseline + matches - excluded
            check(code + '_detection', (row is None if total == 0 else row is not None and row['rows'] == 1 and row['occurrences'] == total))

    # Post-sync severity may differ from the severity that produced the saved AL scores.
    # Exports alone cannot prove pre-sync scoring, impact rate snapshots, or runtime timing.
    check('finding_derived_score', detail='Pre-sync severity plus scan-time enabled-module evidence required')
    check('configured_impact_recalculation', detail='Scan-time impact definitions and hourly rate required')
    status = 'FAIL' if any(c['status'] == 'FAIL' for c in checks) else 'BLOCKED'
    return dict(status=status, readiness='NOT_READY_FOR_LARGE',
                evidence_kind='OFFLINE_EXPORT_RECONCILIATION_NOT_BC_EXECUTION',
                reported_score_arithmetic=dict(numerator=numerator, weight=denominator, score=computed_score),
                inventories=inventories, checks=checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--bc-export', type=Path, help='Original JSON downloaded by the read-only SaaS diagnostic')
    parser.add_argument('--authoritative-runtime', action='store_true', help='Validate the pinned real DEV export directly')
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('Output must not overwrite input evidence')
    raw = args.input.read_bytes()
    data = json.loads(raw.decode('utf-8-sig'), parse_float=Decimal)
    if args.authoritative_runtime:
        require(args.bc_export is None, 'Use direct --input for authoritative runtime')
        require(hashlib.sha256(raw).hexdigest() == EVIDENCE_SHA256, 'Original evidence SHA256 differs')
        result = reconcile_runtime_export(data)
        result['evidence_sha256'] = EVIDENCE_SHA256
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(result['status'] + ': ' + result['gate'] + '; LARGE BLOCKED')
        return 0
    bc_raw = None
    if args.bc_export:
        if args.bc_export.resolve() == args.output.resolve():
            parser.error('Output must not overwrite BC export')
        bc_raw = args.bc_export.read_bytes()
        bc = json.loads(bc_raw.decode('utf-8-sig'), parse_float=Decimal)
        if bc.get('evidence_kind') != 'BC_PERSISTED_FINDINGS_AND_CURRENT_READ_ONLY_ATTRIBUTION':
            parser.error('Not the diagnostic export schema')
        for key in ('company', 'scan_id', 'generator_run_id'):
            if bc['context'][key] != data['context'][key]:
                parser.error('BC export context mismatch')
        data.setdefault('exports', {})['bc'] = bc['exports']['bc']
        data['scenario_observations'] = bc['scenario_observations']
        data['run_snapshot'] = bc['run_snapshot']
    result = reconcile(data)
    result['input_sha256'] = hashlib.sha256(raw).hexdigest()
    if bc_raw is not None:
        result['bc_export_sha256'] = hashlib.sha256(bc_raw).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(result['status'] + ': ' + result['readiness'])
    return 1 if result['status'] == 'FAIL' else 2


if __name__ == '__main__':
    raise SystemExit(main())
