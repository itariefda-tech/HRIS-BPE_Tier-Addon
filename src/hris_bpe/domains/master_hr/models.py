from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hris_bpe.database.base import (
    AuditActorMixin,
    Base,
    PrimaryKeyMixin,
    TimestampMixin,
    VersionedMixin,
)


class Employee(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "employees"
    __table_args__ = (
        Index("ix_employees_company_branch_status", "company_id", "branch_id", "employee_status"),
        Index("ix_employees_branch_status", "branch_id", "employee_status"),
    )

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id"), nullable=True
    )
    position_id: Mapped[int | None] = mapped_column(
        ForeignKey("positions.id"), nullable=True
    )
    employee_number: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(180))
    nik: Mapped[str | None] = mapped_column(String(80), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    address: Mapped[str | None] = mapped_column(Text(), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    marital_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    employment_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    employee_status: Mapped[str] = mapped_column(String(40), default="ACTIVE")
    resign_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    photo_path: Mapped[str | None] = mapped_column(String(255), nullable=True)


class GuardProfile(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "guard_profiles"

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), unique=True, index=True
    )
    guard_registration_number: Mapped[str | None] = mapped_column(String(80), nullable=True)
    guard_level: Mapped[str | None] = mapped_column(String(60), nullable=True)
    uniform_size: Mapped[str | None] = mapped_column(String(10), nullable=True)
    shoe_size: Mapped[str | None] = mapped_column(String(10), nullable=True)
    blood_type: Mapped[str | None] = mapped_column(String(5), nullable=True)
    firearm_license_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    driving_license_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fitness_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    blacklist_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    blacklist_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)


class EmployeeContract(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "employee_contracts"
    __table_args__ = (
        Index("ix_employee_contracts_employee_status_dates", "employee_id", "status", "start_date"),
    )

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    contract_number: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    contract_type: Mapped[str] = mapped_column(String(50))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    salary_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    basic_salary: Mapped[Decimal | None] = mapped_column(Numeric(16, 2), nullable=True)
    allowance_fixed: Mapped[Decimal | None] = mapped_column(Numeric(16, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="ACTIVE")
