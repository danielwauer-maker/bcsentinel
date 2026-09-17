"""Characterizes an existing defect via real API/persistence in the isolated test DB.

These assertions describe the defect, not the desired repair contract. Update the
expected lossless behavior explicitly in the repair sprint. No SaaS connection.
"""
import pytest
import json
from decimal import Decimal
from pathlib import Path

from app.db import SessionLocal
from app.models import Scan, ScanIssueRecord
from test_product_licensing_p0 import _deep_scan_payload


@pytest.mark.parametrize('counts', [(2, 3), (3, 2)])
def test_same_code_groups_keep_last_but_commercial_total_keeps_both(
    client, tenant_factory, auth_header_factory, counts
):
    tenant = tenant_factory(plan='free', license_status='trial')
    payload = _deep_scan_payload(tenant['tenant_id'], 'EXT50C_SYNTHETIC_GROUPS')
    payload.update(scan_type='data_health_score', issues_count=2)
    payload['issues'] = [dict(code='CUSTOMERS_DUPLICATE_EMAIL', category='CUSTOMER', title='Synthetic group',
                              severity='high', affected_count=count, premium_only=False) for count in counts]
    response = client.post('/scan/sync', headers=auth_header_factory(tenant), json=payload)
    assert response.status_code == 200, response.text
    assert len(response.json()['issues']) == 1
    assert response.json()['issues'][0]['affected_count'] == counts[-1]
    assert response.json()['commercials']['estimated_loss_eur'] == 180
    with SessionLocal() as db:
        scan = db.query(Scan).filter_by(scan_id=payload['scan_id']).one()
        issues = db.query(ScanIssueRecord).filter_by(scan_id=payload['scan_id']).all()
        assert scan.issues_count == 2
        assert scan.estimated_loss_eur == 180
        assert len(issues) == 1
        assert issues[0].affected_count == counts[-1]
        assert issues[0].estimated_impact_eur == counts[-1] * 36
    token = client.get('/analytics/get-token', headers=auth_header_factory(tenant))
    assert token.status_code == 200
    dashboard = client.get('/analytics/embed/data', params={'embed_token': token.json()['token']})
    assert dashboard.status_code == 200
    kpis = dashboard.json()['kpis']
    assert kpis['issues_count'] == 2
    assert kpis['affected_records'] == counts[-1]
    assert kpis['estimated_loss_eur'] == 180


def test_real_95_row_fixture_replays_losslessly_in_isolated_backend(
    client, tenant_factory, auth_header_factory
):
    """Real values, synthetic test tenant/run: not a live backend export."""
    root = Path(__file__).resolve().parents[2]
    data = json.loads((root / 'quality/release/ext-50-12c-dev-run1-evidence.json').read_text(encoding='utf-8-sig'))
    tenant = tenant_factory(plan='free', license_status='trial')
    payload = _deep_scan_payload(tenant['tenant_id'], 'EXT50C_LOCAL_REAL_FIXTURE_REPLAY')
    payload.update(scan_type='data_health_score', issues_count=95, checks_count=165, data_score=38,
                   module_scores={k.lower(): v for k, v in data['run_snapshot']['module_scores'].items()})
    payload['issues'] = [dict(code=r['code'], category=r['category'], title=r['check_name'], severity=r['severity'],
                              affected_count=r['affected_count'], premium_only=False) for r in data['exports']['bc']['rows']]
    response = client.post('/scan/sync', headers=auth_header_factory(tenant), json=payload)
    assert response.status_code == 200, response.text
    assert len(response.json()['issues']) == 95
    with SessionLocal() as db:
        issues = db.query(ScanIssueRecord).filter_by(scan_id=payload['scan_id']).all()
        assert len(issues) == 95
        assert sum(r.affected_count for r in issues) == 224999
        assert sum(Decimal(str(r.estimated_impact_eur)) for r in issues) == Decimal('2202021.49')
    token = client.get('/analytics/get-token', headers=auth_header_factory(tenant))
    assert token.status_code == 200
    dashboard = client.get('/analytics/embed/data', params={'embed_token': token.json()['token']})
    assert dashboard.status_code == 200
    kpis = dashboard.json()['kpis']
    for key, value in dict(issues_count=95, affected_records=224999, estimated_loss_eur=2202021.49,
                           potential_saving_eur=1541415.04, health_score=38, checks_run=165).items():
        assert kpis[key] == value
