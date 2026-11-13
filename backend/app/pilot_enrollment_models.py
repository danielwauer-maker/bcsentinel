"""Controlled pilot enrollment; never store plaintext enrollment credentials."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class PilotEnrollment(Base):
    __tablename__ = "pilot_enrollments"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_pilot_enrollment_token_hash"),
        UniqueConstraint("identity_key", name="uq_pilot_enrollment_identity_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    authorized_email: Mapped[str] = mapped_column(String(255), nullable=False)
    identity_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    commercial_profile: Mapped[str] = mapped_column(String(60), nullable=False)
    token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    token_expires_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    registered_tenant_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("tenants.tenant_id"), nullable=True)
    registered_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PilotEnrollmentAudit(Base):
    __tablename__ = "pilot_enrollment_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    enrollment_id: Mapped[int] = mapped_column(Integer, ForeignKey("pilot_enrollments.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
