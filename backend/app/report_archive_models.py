"""Immutable report evidence and one-time BC-native access grants.

A report's retention follows the tenant's retention/deletion policy. One-time
links are credentials, not the report storage mechanism.
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ReportAccessGrant(Base):
    __tablename__ = "report_access_grants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False, index=True)
    company_id: Mapped[str] = mapped_column(String(64), nullable=False)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.scan_id", ondelete="CASCADE"), nullable=False)
    variant: Mapped[str] = mapped_column(String(20), nullable=False)
    expires_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ReportArchive(Base):
    __tablename__ = "report_archives"
    __table_args__ = (
        UniqueConstraint("tenant_id", "company_id", "scan_id", "variant", name="uq_report_archive_identity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False, index=True)
    company_id: Mapped[str] = mapped_column(String(64), nullable=False)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.scan_id", ondelete="CASCADE"), nullable=False)
    variant: Mapped[str] = mapped_column(String(20), nullable=False)
    contract_version: Mapped[str] = mapped_column(String(80), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
