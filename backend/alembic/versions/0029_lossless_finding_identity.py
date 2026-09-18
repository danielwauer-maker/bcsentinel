"""Preserve finding groups independently of check codes.

Downgrade refuses ambiguous multi-group data rather than deleting it.
"""
from alembic import op
import sqlalchemy as sa

revision = '0029_finding_identity'
down_revision = '0028_exception_count'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('scan_issues', sa.Column('finding_id', sa.String(128), nullable=True))
    op.execute(sa.text("UPDATE scan_issues SET finding_id = 'legacy:' || code"))
    with op.batch_alter_table('scan_issues') as batch:
        batch.alter_column('finding_id', existing_type=sa.String(128), nullable=False)
        batch.drop_constraint('uq_scan_issues_scan_code', type_='unique')
        batch.create_unique_constraint('uq_scan_issues_scan_finding', ['scan_id', 'finding_id'])


def downgrade():
    duplicate = op.get_bind().execute(sa.text(
        'SELECT 1 FROM scan_issues GROUP BY scan_id, code HAVING COUNT(*) > 1 LIMIT 1'
    )).first()
    if duplicate:
        raise RuntimeError('Cannot downgrade lossless findings: multiple groups exist. No data has been removed.')
    with op.batch_alter_table('scan_issues') as batch:
        batch.drop_constraint('uq_scan_issues_scan_finding', type_='unique')
        batch.create_unique_constraint('uq_scan_issues_scan_code', ['scan_id', 'code'])
        batch.drop_column('finding_id')
