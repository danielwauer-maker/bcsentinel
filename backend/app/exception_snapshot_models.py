from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ScanExceptionSnapshot(Base):
    __tablename__ = "scan_exception_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "scan_id",
            "source_exception_entry_no",
            name="uq_scan_exception_snapshot_source",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.scan_id", ondelete="CASCADE"), index=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.tenant_id", ondelete="CASCADE"), index=True)
    company_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    source_exception_entry_no: Mapped[int] = mapped_column(Integer)
    table_id: Mapped[int] = mapped_column(Integer)
    record_system_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    record_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    record_caption: Mapped[str | None] = mapped_column(String(150), nullable=True)
    issue_code: Mapped[str] = mapped_column(String(80), index=True)
    reason: Mapped[str] = mapped_column(Text)
    exception_created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    exception_created_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    captured_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
