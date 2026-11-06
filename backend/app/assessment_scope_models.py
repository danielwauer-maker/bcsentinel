from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class AssessmentScopeSnapshot(Base):
    __tablename__ = "assessment_scope_snapshots"
    __table_args__ = (
        UniqueConstraint("scan_id", "version", name="uq_assessment_scope_scan_version"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.scan_id"), index=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.tenant_id"), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    state: Mapped[str] = mapped_column(String(20), default="auto", index=True)
    source: Mapped[str] = mapped_column(String(30), default="usage_detection")
    score_type: Mapped[str] = mapped_column(String(30), default="preliminary")
    score_value: Mapped[int] = mapped_column(Integer, default=100)
    supported_modules_count: Mapped[int] = mapped_column(Integer, default=0)
    included_modules_count: Mapped[int] = mapped_column(Integer, default=0)
    unknown_modules_count: Mapped[int] = mapped_column(Integer, default=0)
    unsupported_extensions_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    confirmed_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    modules: Mapped[list["AssessmentScopeModule"]] = relationship(
        back_populates="snapshot",
        cascade="all, delete-orphan",
    )


class AssessmentScopeModule(Base):
    __tablename__ = "assessment_scope_modules"
    __table_args__ = (
        UniqueConstraint("snapshot_id", "module_code", name="uq_assessment_scope_module"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("assessment_scope_snapshots.id"), index=True)
    module_code: Mapped[str] = mapped_column(String(40), index=True)
    display_name: Mapped[str] = mapped_column(String(80))
    support_status: Mapped[str] = mapped_column(String(20), default="supported")
    detection_status: Mapped[str] = mapped_column(String(20), default="unknown")
    decision: Mapped[str] = mapped_column(String(20), default="inherit")
    included_in_score: Mapped[int] = mapped_column(Integer, default=0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    detection_reason: Mapped[str] = mapped_column(Text, default="")
    module_score: Mapped[int] = mapped_column(Integer, default=100)

    snapshot: Mapped["AssessmentScopeSnapshot"] = relationship(back_populates="modules")


class ValidationScopeBinding(Base):
    """Immutable link between a Validation scan and the confirmed Full scope used as baseline."""

    __tablename__ = "validation_scope_bindings"
    __table_args__ = (
        UniqueConstraint("validation_scan_id", name="uq_validation_scope_validation_scan"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.tenant_id"), index=True)
    validation_scan_id: Mapped[str] = mapped_column(ForeignKey("scans.scan_id"), index=True)
    baseline_scan_id: Mapped[str] = mapped_column(ForeignKey("scans.scan_id"), index=True)
    scope_snapshot_id: Mapped[int] = mapped_column(ForeignKey("assessment_scope_snapshots.id"), index=True)
    scope_version: Mapped[int] = mapped_column(Integer)
    bound_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True))
