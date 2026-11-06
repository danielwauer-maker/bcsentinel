from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ProductMigrationRecord(Base):
    __tablename__ = "product_migration_records"
    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", name="uq_product_migration_entity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(30), index=True)
    entity_id: Mapped[int] = mapped_column(Integer, index=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.tenant_id"), index=True)
    legacy_code: Mapped[str] = mapped_column(String(80), index=True)
    commercial_offer_id: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    billing_variant: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    resolution: Mapped[str] = mapped_column(String(40), index=True)
    rights_preserved: Mapped[bool] = mapped_column(Boolean, default=True)
    migrated_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
