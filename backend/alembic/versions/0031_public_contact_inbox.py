"""Add public contact inbox for Core pilot."""

from alembic import op
import sqlalchemy as sa

revision = "0031_public_contact_inbox"
down_revision = "0030_dashboard_user_security"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "public_contact_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("salutation", sa.String(length=30), nullable=True),
        sa.Column("first_name", sa.String(length=100), nullable=True),
        sa.Column("last_name", sa.String(length=100), nullable=True),
        sa.Column("company", sa.String(length=160), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=60), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("intent", sa.String(length=80), nullable=True),
        sa.Column("language", sa.String(length=10), nullable=True),
        sa.Column("privacy_accepted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("mail_status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("mail_error", sa.Text(), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_public_contact_messages_email", "public_contact_messages", ["email"], unique=False)
    op.create_index("ix_public_contact_messages_intent", "public_contact_messages", ["intent"], unique=False)
    op.create_index("ix_public_contact_messages_mail_status", "public_contact_messages", ["mail_status"], unique=False)
    op.create_index("ix_public_contact_messages_created_at_utc", "public_contact_messages", ["created_at_utc"], unique=False)


def downgrade():
    op.drop_index("ix_public_contact_messages_created_at_utc", table_name="public_contact_messages")
    op.drop_index("ix_public_contact_messages_mail_status", table_name="public_contact_messages")
    op.drop_index("ix_public_contact_messages_intent", table_name="public_contact_messages")
    op.drop_index("ix_public_contact_messages_email", table_name="public_contact_messages")
    op.drop_table("public_contact_messages")
