from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class TenantSupportAccessGrant(Base):
    __tablename__ = "tenant_support_access_grants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False, index=True)
    access_mode: Mapped[str] = mapped_column(String(30), nullable=False, default="diagnostics")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    valid_from_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_until_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    granted_by_user_identity_id: Mapped[int] = mapped_column(ForeignKey("user_identities.id", ondelete="RESTRICT"), nullable=False)
    revoked_by_user_identity_id: Mapped[int | None] = mapped_column(ForeignKey("user_identities.id", ondelete="SET NULL"), nullable=True)
    revoked_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TenantFeatureFlag(Base):
    __tablename__ = "tenant_feature_flags"
    __table_args__ = (UniqueConstraint("tenant_id", "flag_key", name="uq_tenant_feature_flag"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False, index=True)
    flag_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    config_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    updated_by: Mapped[str] = mapped_column(String(160), nullable=False)
    updated_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TenantDataLifecycleRequest(Base):
    __tablename__ = "tenant_data_lifecycle_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False, index=True)
    request_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="requested", index=True)
    requested_by_user_identity_id: Mapped[int] = mapped_column(ForeignKey("user_identities.id", ondelete="RESTRICT"), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requested_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    completed_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    evidence_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class ProductTelemetryEvent(Base):
    __tablename__ = "product_telemetry_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str | None] = mapped_column(ForeignKey("tenants.tenant_id", ondelete="SET NULL"), nullable=True, index=True)
    event_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    outcome: Mapped[str] = mapped_column(String(30), nullable=False, default="info", index=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    occurred_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
