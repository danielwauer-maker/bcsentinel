"""add stable Business Central registration identity

Revision ID: 0022_tenant_registration_identity
Revises: 0021_dashboard_users
Create Date: 2026-07-16 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0022_tenant_registration_identity"
down_revision = "0021_dashboard_users"
branch_labels = None
depends_on = None


def _assert_no_duplicate_dashboard_emails() -> None:
    connection = op.get_bind()
    duplicates = connection.execute(
        sa.text(
            "SELECT lower(email) AS normalized_email, count(*) AS duplicate_count "
            "FROM dashboard_users GROUP BY lower(email) HAVING count(*) > 1"
        )
    ).fetchall()
    if duplicates:
        values = ", ".join(f"{row[0]} ({row[1]})" for row in duplicates)
        raise RuntimeError(
            "Cannot enforce dashboard email uniqueness. Resolve duplicate legacy dashboard users first: "
            + values
        )


def upgrade() -> None:
    _assert_no_duplicate_dashboard_emails()
    with op.batch_alter_table("tenants") as batch_op:
        batch_op.add_column(sa.Column("registration_identity_key", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("entra_tenant_id", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("bc_environment_name", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("bc_environment_type", sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column("bc_company_id", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("bc_company_name", sa.String(length=100), nullable=True))
        batch_op.create_unique_constraint(
            "uq_tenants_registration_identity_key", ["registration_identity_key"]
        )

    op.create_index(
        "ix_tenants_registration_identity_key", "tenants", ["registration_identity_key"], unique=False
    )
    op.create_index("ix_tenants_entra_tenant_id", "tenants", ["entra_tenant_id"], unique=False)
    op.create_index("ix_tenants_bc_company_id", "tenants", ["bc_company_id"], unique=False)
    op.create_index("uq_dashboard_users_email", "dashboard_users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_dashboard_users_email", table_name="dashboard_users")
    op.drop_index("ix_tenants_bc_company_id", table_name="tenants")
    op.drop_index("ix_tenants_entra_tenant_id", table_name="tenants")
    op.drop_index("ix_tenants_registration_identity_key", table_name="tenants")
    with op.batch_alter_table("tenants") as batch_op:
        batch_op.drop_constraint("uq_tenants_registration_identity_key", type_="unique")
        batch_op.drop_column("bc_company_name")
        batch_op.drop_column("bc_company_id")
        batch_op.drop_column("bc_environment_type")
        batch_op.drop_column("bc_environment_name")
        batch_op.drop_column("entra_tenant_id")
        batch_op.drop_column("registration_identity_key")
