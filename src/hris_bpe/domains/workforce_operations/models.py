from __future__ import annotations

from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from hris_bpe.database.base import (
    AuditActorMixin,
    Base,
    PrimaryKeyMixin,
    TimestampMixin,
    VersionedMixin,
)


class EmployeeDeployment(
    Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin
):
    __tablename__ = "employee_deployments"
    __table_args__ = (
        Index(
            "ix_employee_deployments_site_status_dates",
            "client_site_id",
            "deployment_status",
            "start_date",
        ),
        Index("ix_employee_deployments_employee_status", "employee_id", "deployment_status"),
    )

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    client_contract_id: Mapped[int] = mapped_column(ForeignKey("client_contracts.id"))
    client_site_id: Mapped[int] = mapped_column(ForeignKey("client_sites.id"), index=True)
    site_post_id: Mapped[int | None] = mapped_column(ForeignKey("site_posts.id"), nullable=True)
    position_id: Mapped[int | None] = mapped_column(ForeignKey("positions.id"), nullable=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    deployment_status: Mapped[str] = mapped_column(String(40), default="ACTIVE")
    source_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)


class DeploymentHistory(Base, PrimaryKeyMixin):
    __tablename__ = "deployment_histories"
    __table_args__ = (
        Index(
            "ix_deployment_histories_deployment_action_date",
            "employee_deployment_id",
            "action_date",
        ),
    )

    employee_deployment_id: Mapped[int] = mapped_column(
        ForeignKey("employee_deployments.id"), index=True
    )
    action_type: Mapped[str] = mapped_column(String(40), index=True)
    old_client_site_id: Mapped[int | None] = mapped_column(
        ForeignKey("client_sites.id"), nullable=True
    )
    new_client_site_id: Mapped[int | None] = mapped_column(
        ForeignKey("client_sites.id"), nullable=True
    )
    old_site_post_id: Mapped[int | None] = mapped_column(
        ForeignKey("site_posts.id"), nullable=True
    )
    new_site_post_id: Mapped[int | None] = mapped_column(
        ForeignKey("site_posts.id"), nullable=True
    )
    action_date: Mapped[date] = mapped_column(Date, index=True)
    remarks: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ShiftType(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "shift_types"
    __table_args__ = (Index("ix_shift_types_company_code", "company_id", "code"),)

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    cross_day_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    break_minutes: Mapped[int] = mapped_column(Integer, default=0)
    tolerance_late_minutes: Mapped[int] = mapped_column(Integer, default=0)
    overtime_after_minutes: Mapped[int] = mapped_column(Integer, default=480)


class WorkSchedule(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "work_schedules"
    __table_args__ = (
        Index("ix_work_schedules_deployment_date", "employee_deployment_id", "scheduled_date"),
        Index("ix_work_schedules_site_date_status", "client_site_id", "scheduled_date", "schedule_status"),
        Index("ix_work_schedules_employee_date_status", "employee_id", "scheduled_date", "schedule_status"),
    )

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    employee_deployment_id: Mapped[int] = mapped_column(
        ForeignKey("employee_deployments.id"), index=True
    )
    client_site_id: Mapped[int] = mapped_column(ForeignKey("client_sites.id"), index=True)
    site_post_id: Mapped[int | None] = mapped_column(ForeignKey("site_posts.id"), nullable=True)
    shift_type_id: Mapped[int] = mapped_column(ForeignKey("shift_types.id"), index=True)
    scheduled_date: Mapped[date] = mapped_column(Date, index=True)
    scheduled_start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scheduled_end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    schedule_status: Mapped[str] = mapped_column(String(40), default="DRAFT")
    replacement_for_schedule_id: Mapped[int | None] = mapped_column(
        ForeignKey("work_schedules.id"), nullable=True
    )
    generated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
