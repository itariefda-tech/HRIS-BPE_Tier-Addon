from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hris_bpe.database.base import (
    AuditActorMixin,
    Base,
    PrimaryKeyMixin,
    TimestampMixin,
    VersionedMixin,
)


class Client(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "clients"
    __table_args__ = (Index("ix_clients_company_status", "company_id", "status"),)

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(180))
    industry_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contact_person_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    contact_person_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    contact_person_email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    billing_address: Mapped[str | None] = mapped_column(Text(), nullable=True)
    tax_number: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="ACTIVE")


class ClientContract(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "client_contracts"
    __table_args__ = (
        Index("ix_client_contracts_client_status_dates", "client_id", "status", "start_date"),
    )

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    contract_number: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    contract_title: Mapped[str] = mapped_column(String(180))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    contract_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="IDR")
    tax_included_flag: Mapped[bool] = mapped_column(Boolean, default=True)
    payment_term_days: Mapped[int] = mapped_column(Integer, default=30)
    sla_description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="ACTIVE")
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
