"""Offline reconciliation of sanitized exports. No network, SQL, BC writes or credentials."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

WEIGHTS = dict(zip(('System', 'Finance', 'Sales', 'Purchasing', 'Inventory', 'CRM',
                    'Manufacturing', 'Service', 'Jobs', 'HR'), (15, 20, 15, 10, 15, 5, 10, 5, 3, 2)))
EXPECTED = dict(zip(('CUSTOMERS_MISSING_EMAIL', 'VENDORS_MISSING_PHONE',
                     'ITEMS_WITHOUT_UNIT_PRICE', 'ITEMS_WITHOUT_UNIT_COST'), (600, 200, 600, 600)))


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
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('Output must not overwrite input evidence')
    raw = args.input.read_bytes()
    data = json.loads(raw, parse_float=Decimal)
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
