from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class TenantCustomerLifecycle(Base):
    __tablename__ = "tenant_customer_lifecycles"

    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.tenant_id", ondelete="CASCADE"), primary_key=True
    )
    state: Mapped[str] = mapped_column(String(30), nullable=False, default="onboarding", index=True)
    effective_from_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    grace_until_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pilot_until_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_by: Mapped[str] = mapped_column(String(160), nullable=False)
    updated_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TenantBillingProfile(Base):
    __tablename__ = "tenant_billing_profiles"

    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.tenant_id", ondelete="CASCADE"), primary_key=True
    )
    legal_company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    billing_email: Mapped[str] = mapped_column(String(320), nullable=False)
    address_line1: Mapped[str] = mapped_column(String(200), nullable=False)
    address_line2: Mapped[str | None] = mapped_column(String(200), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(30), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    vat_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    tax_treatment: Mapped[str] = mapped_column(String(40), nullable=False, default="provider_determined")
    provider_customer_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    provider_tax_evidence_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_by: Mapped[str] = mapped_column(String(160), nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TenantConnectionDiagnostic(Base):
    __tablename__ = "tenant_connection_diagnostics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False, index=True
    )
    environment_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    extension_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    bc_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    api_reachable: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    permissions_ok: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    compatibility_status: Mapped[str] = mapped_column(String(30), nullable=False, default="unknown")
    upgrade_required: Mapped[str] = mapped_column(String(10), nullable=False, default="false")
    diagnostic_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    observed_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
