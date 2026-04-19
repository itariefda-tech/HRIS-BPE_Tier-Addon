from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from hris_bpe.database.base import (
    AuditActorMixin,
    Base,
    PrimaryKeyMixin,
    TimestampMixin,
    VersionedMixin,
)


class Company(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "companies"
    __table_args__ = (Index("ix_companies_status_code", "status", "code"),)

    code: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    legal_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    tax_number: Mapped[str | None] = mapped_column(String(60), nullable=True)
    address: Mapped[str | None] = mapped_column(Text(), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="ACTIVE")


class Branch(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "branches"
    __table_args__ = (
        UniqueConstraint("company_id", "code"),
        Index("ix_branches_company_status", "company_id", "status"),
    )

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(60))
    name: Mapped[str] = mapped_column(String(150))
    address: Mapped[str | None] = mapped_column(Text(), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    province: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="ACTIVE")


class Department(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint("company_id", "code"),
        Index("ix_departments_company_name", "company_id", "name"),
    )

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(60))
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)


class Position(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "positions"
    __table_args__ = (
        UniqueConstraint("company_id", "code"),
        Index("ix_positions_company_category", "company_id", "category"),
    )

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(60))
    name: Mapped[str] = mapped_column(String(150))
    category: Mapped[str | None] = mapped_column(String(60), nullable=True)
    level_order: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
