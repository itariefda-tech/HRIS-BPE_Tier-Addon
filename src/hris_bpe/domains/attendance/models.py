from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from hris_bpe.database.base import (
    AuditActorMixin,
    Base,
    PrimaryKeyMixin,
    TimestampMixin,
    VersionedMixin,
)


class AttendanceRecord(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("work_schedule_id"),
        Index("ix_attendance_records_employee_date", "employee_id", "attendance_date"),
        Index("ix_attendance_records_site_date_status", "client_site_id", "attendance_date", "attendance_status"),
    )

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    work_schedule_id: Mapped[int] = mapped_column(ForeignKey("work_schedules.id"), index=True)
    client_site_id: Mapped[int] = mapped_column(ForeignKey("client_sites.id"), index=True)
    site_post_id: Mapped[int | None] = mapped_column(ForeignKey("site_posts.id"), nullable=True)
    attendance_date: Mapped[date] = mapped_column(Date, index=True)
    check_in_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    check_out_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    check_in_latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    check_in_longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    check_out_latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    check_out_longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    check_in_photo_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    check_out_photo_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    check_in_method: Mapped[str | None] = mapped_column(String(40), nullable=True)
    check_out_method: Mapped[str | None] = mapped_column(String(40), nullable=True)
    gps_valid_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    face_valid_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    geofence_valid_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    attendance_status: Mapped[str] = mapped_column(String(40), default="SCHEDULED")
    minutes_late: Mapped[int] = mapped_column(Integer, default=0)
    working_minutes: Mapped[int] = mapped_column(Integer, default=0)
    overtime_minutes: Mapped[int] = mapped_column(Integer, default=0)
    remarks: Mapped[str | None] = mapped_column(Text(), nullable=True)


class AttendanceManualAdjustment(Base, PrimaryKeyMixin):
    __tablename__ = "attendance_manual_adjustments"

    attendance_record_id: Mapped[int] = mapped_column(
        ForeignKey("attendance_records.id"), index=True
    )
    old_check_in_datetime: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    new_check_in_datetime: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    old_check_out_datetime: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    new_check_out_datetime: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reason: Mapped[str] = mapped_column(Text())
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AttendanceException(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "attendance_exceptions"
    __table_args__ = (
        Index(
            "ix_attendance_exceptions_record_resolution",
            "attendance_record_id",
            "resolution_status",
        ),
    )

    attendance_record_id: Mapped[int] = mapped_column(
        ForeignKey("attendance_records.id"), index=True
    )
    exception_type: Mapped[str] = mapped_column(String(60), index=True)
    description: Mapped[str] = mapped_column(Text())
    resolution_status: Mapped[str] = mapped_column(String(40), default="OPEN", index=True)
    resolved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AttendanceQrSession(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "attendance_qr_sessions"
    __table_args__ = (
        UniqueConstraint("token_hash"),
        Index(
            "ix_attendance_qr_sessions_schedule_action_status",
            "work_schedule_id",
            "attendance_action",
            "consumed_at",
            "expires_at",
        ),
    )

    work_schedule_id: Mapped[int] = mapped_column(ForeignKey("work_schedules.id"), index=True)
    attendance_action: Mapped[str] = mapped_column(String(20), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consumed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text(), nullable=True)
