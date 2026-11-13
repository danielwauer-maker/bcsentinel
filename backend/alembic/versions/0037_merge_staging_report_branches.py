"""Merge DEV/staging and Full-report migration lineages without data loss.

Revision ID: 0037_merge_staging_report
Revises: 0031_public_contact_inbox, 0036_report_archives

This merge revision has no DDL. It expresses that both independent schema
histories must be present before running the combined application.
NEVER stamp a production or DEV DB across an unexecuted lineage.
"""
revision = "0037_merge_staging_report"
down_revision = ("0031_public_contact_inbox", "0036_report_archives")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
