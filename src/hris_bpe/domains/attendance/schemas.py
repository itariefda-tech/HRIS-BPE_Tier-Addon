from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AttendanceCheckRequest(BaseModel):
    work_schedule_id: int
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    method: str = "gps"
    photo_path: str | None = None
    remarks: str | None = None


class AttendanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    work_schedule_id: int
    client_site_id: int
    site_post_id: int | None
    attendance_date: date
    check_in_datetime: datetime | None
    check_out_datetime: datetime | None
    check_in_latitude: Decimal | None
    check_in_longitude: Decimal | None
    check_out_latitude: Decimal | None
    check_out_longitude: Decimal | None
    check_in_photo_path: str | None
    check_out_photo_path: str | None
    check_in_method: str | None
    check_out_method: str | None
    gps_valid_flag: bool
    face_valid_flag: bool
    geofence_valid_flag: bool
    attendance_status: str
    minutes_late: int
    working_minutes: int
    overtime_minutes: int
    remarks: str | None
    created_at: datetime
    updated_at: datetime


class AttendanceManualAdjustmentCreateRequest(BaseModel):
    attendance_record_id: int
    new_check_in_datetime: datetime | None = None
    new_check_out_datetime: datetime | None = None
    reason: str


class AttendanceManualAdjustmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attendance_record_id: int
    old_check_in_datetime: datetime | None
    new_check_in_datetime: datetime | None
    old_check_out_datetime: datetime | None
    new_check_out_datetime: datetime | None
    reason: str
    approved_by: int | None
    created_by: int | None
    created_at: datetime


class AttendanceExceptionCreateRequest(BaseModel):
    attendance_record_id: int
    exception_type: str
    description: str


class AttendanceExceptionResolveRequest(BaseModel):
    resolution_status: str


class AttendanceExceptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attendance_record_id: int
    exception_type: str
    description: str
    resolution_status: str
    resolved_by: int | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime
