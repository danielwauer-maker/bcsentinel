"""Lossless group matrix, using only the repository's isolated test database."""
import copy
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from app.db import SessionLocal
from app.models import ScanIssueRecord, Tenant, Subscription
from app.services.executive_report_service import build_executive_report, render_executive_report_html
from test_product_licensing_p0 import _deep_scan_payload


def payload(tenant, run='IDENTITY_RUN', groups=2, explicit=True):
    data = _deep_scan_payload(tenant['tenant_id'], run)
    data.update(scan_type='data_health_score', issues_count=groups)
    data['issues'] = [dict(code='CUSTOMERS_DUPLICATE_EMAIL', category='CUSTOMER', title='Group',
                           severity='high', affected_count=i + 2, premium_only=True,
                           **({'finding_id': str(UUID(int=i + 1))} if explicit else {})) for i in range(groups)]
    return data


def sync(client, headers, data):
    result = client.post('/scan/sync', headers=headers, json=data)
    assert result.status_code == 200, result.text
    return result.json()


@pytest.mark.parametrize('groups', [1, 2, 3, 1000])
def test_all_groups_retry_reorder_update_and_sums(client, tenant_factory, auth_header_factory, groups):
    tenant = tenant_factory()
    headers = auth_header_factory(tenant)
    data = payload(tenant, groups=groups)
    first = sync(client, headers, data)
    assert len(first['issues']) == groups
    total = sum(i + 2 for i in range(groups))
    assert Decimal(str(first['commercials']['estimated_loss_eur'])) == total * 36
    with SessionLocal() as db:
        before = {i.finding_id: i.id for i in db.query(ScanIssueRecord).all()}
    data['issues'].reverse()
    second = sync(client, headers, data)
    assert {i['finding_id']: i['estimated_impact_eur'] for i in first['issues']} == {
        i['finding_id']: i['estimated_impact_eur'] for i in second['issues']}
    with SessionLocal() as db:
        rows = db.query(ScanIssueRecord).all()
        assert {i.finding_id: i.id for i in rows} == before
        assert sum(i.affected_count for i in rows) == total
        assert sum(i.estimated_impact_eur for i in rows) == total * 36
    # Same persisted group legitimately updates in a complete snapshot.
    data['issues'][0]['affected_count'] += 1
    updated = sync(client, headers, data)
    assert len(updated['issues']) == groups
    assert updated['commercials']['estimated_loss_eur'] == (total + 1) * 36


@pytest.mark.parametrize('identical', [False, True])
def test_legacy_multiset_is_lossless_and_retry_stable(client, tenant_factory, auth_header_factory, identical):
    tenant = tenant_factory()
    data = payload(tenant, explicit=False)
    if identical:
        data['issues'][1] = copy.deepcopy(data['issues'][0])
    headers = auth_header_factory(tenant)
    first = sync(client, headers, data)
    data['issues'].reverse()
    second = sync(client, headers, data)
    assert len(first['issues']) == len(second['issues']) == 2
    assert {i['finding_id'] for i in first['issues']} == {i['finding_id'] for i in second['issues']}
    with SessionLocal() as db:
        assert db.query(ScanIssueRecord).count() == 2


@pytest.mark.parametrize('attack', ['duplicate_id', 'malformed_id', 'change_check'])
def test_manipulated_identity_rejected_without_overwrite(client, tenant_factory, auth_header_factory, attack):
    tenant = tenant_factory()
    data = payload(tenant)
    headers = auth_header_factory(tenant)
    sync(client, headers, data)
    if attack == 'duplicate_id':
        data['issues'][1]['finding_id'] = data['issues'][0]['finding_id']
    elif attack == 'malformed_id':
        data['issues'][0]['finding_id'] = '../other-tenant'
    else:
        data['issues'][0]['code'] = 'VENDORS_DUPLICATE_EMAIL'
    result = client.post('/scan/sync', headers=headers, json=data)
    assert result.status_code == (409 if attack == 'change_check' else 422)
    with SessionLocal() as db:
        rows = db.query(ScanIssueRecord).all()
        assert len(rows) == 2
        assert {r.code for r in rows} == {'CUSTOMERS_DUPLICATE_EMAIL'}
        assert sum(r.affected_count for r in rows) == 5


def test_two_company_registrations_same_ids_and_cross_tenant_attack(client, tenant_factory, auth_header_factory):
    first, second = tenant_factory(), tenant_factory()
    with SessionLocal() as db:
        for info, company in ((first, 'COMPANY_A'), (second, 'COMPANY_B')):
            tenant = db.query(Tenant).filter_by(tenant_id=info['tenant_id']).one()
            tenant.entra_tenant_id = 'SAME_ENTRA_TENANT'
            tenant.bc_company_id = company
            tenant.registration_identity_key = company
        db.commit()
    sync(client, auth_header_factory(first), payload(first, 'RUN_A'))
    sync(client, auth_header_factory(second), payload(second, 'RUN_B'))
    attack = payload(second, 'RUN_A')
    response = client.post('/scan/sync', headers=auth_header_factory(second), json=attack)
    assert response.status_code == 409
    response = client.post('/scan/sync', headers=auth_header_factory(second), json=payload(first, 'RUN_A'))
    assert response.status_code == 400
    with SessionLocal() as db:
        assert db.query(ScanIssueRecord).count() == 4
        assert db.query(ScanIssueRecord).filter_by(scan_id='RUN_A').count() == 2
        assert db.query(ScanIssueRecord).filter_by(scan_id='RUN_B').count() == 2


def test_two_runs_same_tenant_keep_history(client, tenant_factory, auth_header_factory, subscription_factory):
    tenant = tenant_factory(plan='premium', license_status='active')
    subscription_factory(tenant_id=tenant['tenant_id'])
    with SessionLocal() as db:
        sub = db.query(Subscription).filter_by(tenant_id=tenant['tenant_id']).one()
        sub.plan_code = 'monitoring_monthly'
        sub.current_period_end_utc = datetime.now(timezone.utc) + timedelta(days=30)
        db.commit()
    for run in ('RUN_1', 'RUN_2'):
        data = payload(tenant, run)
        data['scan_type'] = 'monitoring'
        sync(client, auth_header_factory(tenant), data)
    with SessionLocal() as db:
        assert db.query(ScanIssueRecord).count() == 4


@pytest.mark.parametrize('premium', [False, True])
def test_dashboard_and_report_keep_groups_with_access_boundary(
    client, tenant_factory, auth_header_factory, product_access_factory, premium
):
    tenant = tenant_factory(plan='premium' if premium else 'free', license_status='active' if premium else 'trial')
    if premium:
        product_access_factory(tenant_id=tenant['tenant_id'])
    headers = auth_header_factory(tenant)
    sync(client, headers, payload(tenant))
    token = client.get('/analytics/get-token', headers=headers).json()['token']
    response = client.get('/analytics/embed/data', params={'embed_token': token})
    assert response.status_code == 200
    data = response.json()
    assert data['kpis']['affected_records'] == 5
    assert data['kpis']['estimated_loss_eur'] == 180
    if premium:
        assert len(data['top_findings']) == 2
        assert len({r['finding_id'] for r in data['top_findings']}) == 2
        assert {r['finding_id'] for r in data['actions_page']['items']} == {r['finding_id'] for r in data['top_findings']}
    else:
        assert data['top_findings'] == []
        assert data['actions_page']['items'] == []
        for row in data['free_insights']['top_findings']:
            assert not {'code', 'finding_id', 'recommendation_preview', 'open_in_bc_url'} & set(row)
    with SessionLocal() as db:
        saved_tenant = db.query(Tenant).filter_by(tenant_id=tenant['tenant_id']).one()
        report = build_executive_report(db, saved_tenant, 'IDENTITY_RUN')
        assert report.affected_records == 5
        assert report.estimated_loss_eur == 180
        for language in ('en', 'de'):
            saved_tenant.preferred_language = language
            report = build_executive_report(db, saved_tenant, 'IDENTITY_RUN')
            html = render_executive_report_html(report, inline_css=True)
            assert ('<h3>Prüftreffer</h3>' if language == 'de' else '<h3>Check occurrences</h3>') in html
            assert 'Betroffene Datensätze' not in html
            assert 'Affected Records' not in html
