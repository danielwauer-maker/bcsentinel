"""add dashboard user tenant memberships

Revision ID: 0025_dashboard_memberships
Revises: 0024_scan_lifecycle_recovery
Create Date: 2026-07-20 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0025_dashboard_memberships"
down_revision = "0024_scan_lifecycle_recovery"
branch_labels = None
depends_on = None


def _assert_upgrade_is_safe() -> None:
    connection = op.get_bind()
    orphan_count = connection.execute(
        sa.text(
            "SELECT COUNT(*) FROM dashboard_users u "
            "LEFT JOIN tenants t ON t.tenant_id = u.tenant_id "
            "WHERE u.tenant_id IS NULL OR t.tenant_id IS NULL"
        )
    ).scalar_one()
    duplicate_count = connection.execute(
        sa.text(
            "SELECT COUNT(*) FROM ("
            "SELECT lower(trim(email)) AS normalized_email FROM dashboard_users "
            "GROUP BY lower(trim(email)) HAVING COUNT(*) > 1"
            ") AS duplicate_dashboard_emails"
        )
    ).scalar_one()
    invalid_email_count = connection.execute(
        sa.text(
            "SELECT COUNT(*) FROM dashboard_users "
            "WHERE email IS NULL OR trim(email) = ''"
        )
    ).scalar_one()

    if orphan_count or duplicate_count or invalid_email_count:
        raise RuntimeError(
            "Dashboard membership migration stopped because legacy consistency checks failed "
            f"(orphan_users={orphan_count}, normalized_email_conflicts={duplicate_count}, "
            f"invalid_emails={invalid_email_count}). Resolve the counts without logging email values."
        )


def upgrade() -> None:
    _assert_upgrade_is_safe()

    with op.batch_alter_table("dashboard_users") as batch_op:
        batch_op.add_column(sa.Column("normalized_email", sa.String(length=255), nullable=True))

    op.execute(sa.text("UPDATE dashboard_users SET normalized_email = lower(trim(email))"))

    with op.batch_alter_table("dashboard_users") as batch_op:
        batch_op.alter_column("normalized_email", existing_type=sa.String(length=255), nullable=False)
    op.create_index(
        "uq_dashboard_users_normalized_email",
        "dashboard_users",
        ["normalized_email"],
        unique=True,
    )

    op.create_table(
        "dashboard_user_tenant_memberships",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dashboard_user_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(length=50), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_selected_at_utc", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["dashboard_user_id"], ["dashboard_users.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.tenant_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "dashboard_user_id",
            "tenant_id",
            name="uq_dashboard_user_tenant_membership",
        ),
    )
    op.create_index(
        "ix_dashboard_memberships_dashboard_user_id",
        "dashboard_user_tenant_memberships",
        ["dashboard_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_dashboard_memberships_tenant_id",
        "dashboard_user_tenant_memberships",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_dashboard_memberships_is_active",
        "dashboard_user_tenant_memberships",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        "ix_dashboard_memberships_last_selected_at_utc",
        "dashboard_user_tenant_memberships",
        ["last_selected_at_utc"],
        unique=False,
    )

    op.execute(
        sa.text(
            "INSERT INTO dashboard_user_tenant_memberships "
            "(dashboard_user_id, tenant_id, role, is_active, created_at_utc, updated_at_utc) "
            "SELECT id, tenant_id, 'owner', true, created_at_utc, updated_at_utc "
            "FROM dashboard_users"
        )
    )

    op.drop_index(op.f("ix_dashboard_users_tenant_id"), table_name="dashboard_users")
    with op.batch_alter_table("dashboard_users") as batch_op:
        batch_op.drop_constraint("uq_dashboard_users_tenant_email", type_="unique")
        batch_op.drop_column("tenant_id")


def _assert_downgrade_is_safe() -> None:
    connection = op.get_bind()
    incompatible_users = connection.execute(
        sa.text(
            "SELECT COUNT(*) FROM ("
            "SELECT dashboard_user_id FROM dashboard_user_tenant_memberships "
            "GROUP BY dashboard_user_id HAVING COUNT(*) <> 1"
            ") AS incompatible_memberships"
        )
    ).scalar_one()
    users_without_membership = connection.execute(
        sa.text(
            "SELECT COUNT(*) FROM dashboard_users u "
            "LEFT JOIN dashboard_user_tenant_memberships m ON m.dashboard_user_id = u.id "
            "WHERE m.id IS NULL"
        )
    ).scalar_one()
    if incompatible_users or users_without_membership:
        raise RuntimeError(
            "Dashboard membership downgrade stopped because the legacy one-user/one-tenant model "
            "cannot represent the current memberships "
            f"(multi_or_invalid_users={incompatible_users}, users_without_membership={users_without_membership})."
        )


def downgrade() -> None:
    _assert_downgrade_is_safe()

    with op.batch_alter_table("dashboard_users") as batch_op:
        batch_op.add_column(sa.Column("tenant_id", sa.String(length=50), nullable=True))

    op.execute(
        sa.text(
            "UPDATE dashboard_users SET tenant_id = ("
            "SELECT tenant_id FROM dashboard_user_tenant_memberships m "
            "WHERE m.dashboard_user_id = dashboard_users.id)"
        )
    )

    with op.batch_alter_table("dashboard_users") as batch_op:
        batch_op.alter_column("tenant_id", existing_type=sa.String(length=50), nullable=False)
        batch_op.create_foreign_key(
            "fk_dashboard_users_tenant_id_tenants",
            "tenants",
            ["tenant_id"],
            ["tenant_id"],
        )
        batch_op.create_unique_constraint(
            "uq_dashboard_users_tenant_email",
            ["tenant_id", "email"],
        )
    op.create_index(
        op.f("ix_dashboard_users_tenant_id"),
        "dashboard_users",
        ["tenant_id"],
        unique=False,
    )

    op.drop_index(
        "ix_dashboard_memberships_last_selected_at_utc",
        table_name="dashboard_user_tenant_memberships",
    )
    op.drop_index("ix_dashboard_memberships_is_active", table_name="dashboard_user_tenant_memberships")
    op.drop_index("ix_dashboard_memberships_tenant_id", table_name="dashboard_user_tenant_memberships")
    op.drop_index(
        "ix_dashboard_memberships_dashboard_user_id",
        table_name="dashboard_user_tenant_memberships",
    )
    op.drop_table("dashboard_user_tenant_memberships")
    op.drop_index("uq_dashboard_users_normalized_email", table_name="dashboard_users")
    with op.batch_alter_table("dashboard_users") as batch_op:
        batch_op.drop_column("normalized_email")
