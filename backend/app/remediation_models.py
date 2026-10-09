from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class RemediationActionRead(Base):
    __tablename__ = "remediation_actions_read"
    __table_args__ = (UniqueConstraint("tenant_id", "action_id", name="uq_remediation_action_tenant_action"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    action_id: Mapped[str] = mapped_column(String(50), index=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.tenant_id"), index=True)
    company_id: Mapped[str] = mapped_column(String(100), index=True)
    finding_key: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text, default="")
    recommendation_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), index=True)
    priority: Mapped[str] = mapped_column(String(20), index=True)
    owner_principal_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    owner_display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    due_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    started_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    blocked_reason: Mapped[str | None] = mapped_column(String(250), nullable=True)
    completion_note: Mapped[str | None] = mapped_column(String(250), nullable=True)
    validation_result_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(String(30), default="manual")
    created_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    synced_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class RemediationAuditRead(Base):
    __tablename__ = "remediation_audit_read"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    action_id: Mapped[str] = mapped_column(String(50), index=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.tenant_id"), index=True)
    company_id: Mapped[str] = mapped_column(String(100), index=True)
    changed_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    changed_by_principal_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    changed_field_or_status: Mapped[str] = mapped_column(String(100))
    previous_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
