from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class TenantOperatorAction(Base):
    __tablename__ = "tenant_operator_actions"
    __table_args__ = (
        UniqueConstraint(
            "sales_channel",
            "external_order_reference",
            "action_type",
            name="uq_tenant_operator_action_channel_order_action",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.tenant_id", ondelete="CASCADE"), index=True
    )
    action_type: Mapped[str] = mapped_column(String(50), index=True)
    product_code: Mapped[str] = mapped_column(String(50))
    sales_channel: Mapped[str] = mapped_column(String(30), index=True, default="direct")
    external_order_reference: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    entitlement_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenant_product_entitlements.id", ondelete="SET NULL"), nullable=True
    )
    credit_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenant_scan_credits.id", ondelete="SET NULL"), nullable=True
    )
    related_scan_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor: Mapped[str] = mapped_column(String(120))
    created_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
