"""Existing-row preservation and guarded rollback on SQLite and real PostgreSQL."""
import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


@pytest.mark.parametrize('dialect', ['sqlite', 'postgresql'])
def test_upgrade_downgrade_upgrade_preserves_existing_findings(tmp_path, dialect):
    url = f"sqlite:///{(tmp_path / 'finding-migration-test.sqlite3').as_posix()}"
    if dialect == 'postgresql':
        url = os.environ.get('BCSENTINEL_FINDING_MIGRATION_TEST_URL', '')
        if not url:
            pytest.skip('Dedicated PostgreSQL migration test URL not configured; no SQLite substitution')
        assert make_url(url).drivername.startswith('postgresql')
        assert make_url(url).database.endswith('_test'), 'Dedicated test database required'
    env = dict(os.environ, DATABASE_URL=url)
    root = Path(__file__).resolve().parents[1]

    def migrate(command, revision, success=True):
        result = subprocess.run([sys.executable, '-m', 'alembic', command, revision], cwd=root,
                                env=env, text=True, capture_output=True, timeout=120)
        assert (result.returncode == 0) == success, result.stdout + result.stderr
        return result

    migrate('upgrade', '0028_exception_count')
    engine = create_engine(url)
    with engine.begin() as db:
        db.execute(text("INSERT INTO tenants (tenant_id,environment_name,app_version,created_at_utc,current_plan,license_status) "
                        "VALUES ('finding_test_tenant','Test','1.0.2.20','2026-01-01','free','trial')"))
        db.execute(text("INSERT INTO scans (scan_id,tenant_id,scan_type,generated_at_utc,data_score,checks_count,issues_count,summary_headline,summary_rating) "
                        "VALUES ('finding_test_scan','finding_test_tenant','deep','2026-01-01',38,165,1,'Test','Test')"))
        db.execute(text("INSERT INTO scan_issues (scan_id,code,title,severity,affected_count,estimated_impact_eur) "
                        "VALUES ('finding_test_scan','CHECK_A','Original','high',2,72)"))
        before = db.execute(text('SELECT id,scan_id,code,title,severity,affected_count,estimated_impact_eur FROM scan_issues')).all()
    for direction, revision in [('upgrade', 'head'), ('downgrade', '0028_exception_count'), ('upgrade', 'head')]:
        migrate(direction, revision)
        with engine.connect() as db:
            assert db.execute(text('SELECT id,scan_id,code,title,severity,affected_count,estimated_impact_eur FROM scan_issues')).all() == before
    with engine.begin() as db:
        assert db.execute(text('SELECT finding_id FROM scan_issues')).scalar_one() == 'legacy:CHECK_A'
        db.execute(text("INSERT INTO scan_issues (scan_id,finding_id,code,title,severity,affected_count,estimated_impact_eur) "
                        "VALUES ('finding_test_scan','second-group','CHECK_A','Second','high',3,108)"))
    rejected = migrate('downgrade', '0028_exception_count', success=False)
    assert 'Cannot downgrade lossless findings' in rejected.stderr
    with engine.connect() as db:
        assert db.execute(text('SELECT COUNT(*) FROM scan_issues')).scalar_one() == 2
        assert db.execute(text('SELECT SUM(affected_count) FROM scan_issues')).scalar_one() == 5
        assert db.execute(text('SELECT SUM(estimated_impact_eur) FROM scan_issues')).scalar_one() == 180
        assert db.execute(text('SELECT version_num FROM alembic_version')).scalar_one() == '0029_finding_identity'
    engine.dispose()
