from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class NotificationSettingsRead(Base):
    __tablename__ = "notification_settings_read"
    __table_args__ = (
        UniqueConstraint("tenant_id", "company_id", name="uq_notification_settings_tenant_company"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.tenant_id"), index=True)
    company_id: Mapped[str] = mapped_column(String(100), index=True)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en")
    configured_event_types_json: Mapped[str] = mapped_column(Text, default="[]")
    enabled_event_types_json: Mapped[str] = mapped_column(Text, default="[]")
    recipient_count: Mapped[int] = mapped_column(Integer, default=0)
    enabled_recipient_count: Mapped[int] = mapped_column(Integer, default=0)
    channels_json: Mapped[str] = mapped_column(Text, default="[]")
    template_languages_json: Mapped[str] = mapped_column(Text, default="[]")
    sent_deliveries: Mapped[int] = mapped_column(Integer, default=0)
    failed_deliveries: Mapped[int] = mapped_column(Integer, default=0)
    suppressed_deliveries: Mapped[int] = mapped_column(Integer, default=0)
    last_successful_delivery_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_failed_delivery_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    safe_last_failure_summary: Mapped[str | None] = mapped_column(String(250), nullable=True)
    bc_updated_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    synced_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
