from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class PilotInterest(Base):
    __tablename__ = "pilot_interests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    contact_name: Mapped[str] = mapped_column(String(120))
    contact_email: Mapped[str] = mapped_column(String(255), index=True)
    company_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    bc_context: Mapped[str | None] = mapped_column(String(80), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="de")
    source_page: Mapped[str] = mapped_column(String(120), default="pilot")
    status: Mapped[str] = mapped_column(String(20), default="new", index=True)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
