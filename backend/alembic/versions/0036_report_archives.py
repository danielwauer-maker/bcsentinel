"""BC-native report history and one-time browser grants.

Revision ID: 0036_report_archives
Revises: 0035_scan_company_lcy
"""
from alembic import op
import sqlalchemy as sa

revision = "0036_report_archives"
down_revision = "0035_scan_company_lcy"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "report_archives",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", sa.String(length=64), nullable=False),
        sa.Column("scan_id", sa.String(length=50), sa.ForeignKey("scans.scan_id", ondelete="CASCADE"), nullable=False),
        sa.Column("variant", sa.String(length=20), nullable=False),
        sa.Column("contract_version", sa.String(length=80), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "company_id", "scan_id", "variant", name="uq_report_archive_identity"),
    )
    op.create_index("ix_report_archives_tenant_id", "report_archives", ["tenant_id"])
    op.create_table(
        "report_access_grants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("tenant_id", sa.String(length=50), sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", sa.String(length=64), nullable=False),
        sa.Column("scan_id", sa.String(length=50), sa.ForeignKey("scans.scan_id", ondelete="CASCADE"), nullable=False),
        sa.Column("variant", sa.String(length=20), nullable=False),
        sa.Column("expires_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at_utc", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_report_access_grants_token_hash", "report_access_grants", ["token_hash"], unique=True)
    op.create_index("ix_report_access_grants_tenant_id", "report_access_grants", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_report_access_grants_tenant_id", table_name="report_access_grants")
    op.drop_index("ix_report_access_grants_token_hash", table_name="report_access_grants")
    op.drop_table("report_access_grants")
    op.drop_index("ix_report_archives_tenant_id", table_name="report_archives")
    op.drop_table("report_archives")
