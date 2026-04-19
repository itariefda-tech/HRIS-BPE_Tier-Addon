from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hris_bpe.common.dependencies import CurrentUserContext
from hris_bpe.common.helpers import utc_now
from hris_bpe.common.scope import (
    ensure_company_access,
    filter_items_by_company_scope,
    has_unscoped_permission,
)
from hris_bpe.common.security import haversine_distance_meters
from hris_bpe.domains.attendance.models import (
    AttendanceException,
    AttendanceManualAdjustment,
    AttendanceRecord,
)
from hris_bpe.domains.attendance.repository import AttendanceRepository
from hris_bpe.domains.attendance.schemas import (
    AttendanceCheckRequest,
    AttendanceExceptionCreateRequest,
    AttendanceExceptionResolveRequest,
    AttendanceManualAdjustmentCreateRequest,
)
from hris_bpe.domains.master_hr.models import Employee
from hris_bpe.domains.site_operations.models import ClientSite
from hris_bpe.domains.workforce_operations.models import ShiftType, WorkSchedule


class AttendanceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AttendanceRepository(db)

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def list_records(self, current_user: CurrentUserContext):
        employee_company_map = {
            employee.id: employee.company_id for employee in self.db.query(Employee).all()
        }
        items = filter_items_by_company_scope(
            current_user,
            self.repository.list_records(),
            lambda item: employee_company_map.get(item.employee_id),
        )
        if has_unscoped_permission(current_user, "attendance.manage"):
            return items
        if current_user.site_scope_ids:
            items = [item for item in items if item.client_site_id in current_user.site_scope_ids]
        if current_user.branch_scope_ids:
            employee_map = {
                employee.id: employee.branch_id for employee in self.db.query(Employee).all()
            }
            items = [
                item
                for item in items
                if employee_map.get(item.employee_id) in current_user.branch_scope_ids
            ]
        if current_user.user.employee_id is not None and "attendance.manage" not in current_user.permission_codes:
            items = [item for item in items if item.employee_id == current_user.user.employee_id]
        return items

    def list_exceptions(self, current_user: CurrentUserContext):
        allowed_record_ids = {item.id for item in self.list_records(current_user)}
        return [
            item
            for item in self.repository.list_exceptions()
            if item.attendance_record_id in allowed_record_ids
        ]

    def list_manual_adjustments(self, current_user: CurrentUserContext):
        allowed_record_ids = {item.id for item in self.list_records(current_user)}
        return [
            item
            for item in self.repository.list_manual_adjustments()
            if item.attendance_record_id in allowed_record_ids
        ]

    def _load_schedule(self, schedule_id: int) -> WorkSchedule:
        schedule = self.db.get(WorkSchedule, schedule_id)
        if schedule is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Work schedule tidak ditemukan.",
            )
        return schedule

    def _ensure_schedule_access(
        self, current_user: CurrentUserContext, schedule: WorkSchedule
    ) -> None:
        employee = self.db.get(Employee, schedule.employee_id)
        if employee is not None:
            ensure_company_access(
                current_user,
                employee.company_id,
                detail="Schedule tidak berada dalam scope company user.",
            )
        if has_unscoped_permission(current_user, "attendance.manage"):
            return
        if current_user.site_scope_ids and schedule.client_site_id not in current_user.site_scope_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Schedule tidak berada dalam scope site user.",
            )
        if current_user.branch_scope_ids:
            if employee is None or employee.branch_id not in current_user.branch_scope_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Schedule tidak berada dalam scope branch user.",
                )
        if "attendance.manage" in current_user.permission_codes:
            return
        if current_user.user.employee_id != schedule.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Schedule tidak berada dalam scope user.",
            )

    def _geofence_flags(
        self, schedule: WorkSchedule, payload: AttendanceCheckRequest
    ) -> tuple[bool, bool]:
        if payload.latitude is None or payload.longitude is None:
            return False, False
        site = self.db.get(ClientSite, schedule.client_site_id)
        if site is None or site.latitude is None or site.longitude is None or site.radius_meters is None:
            return True, True
        distance = haversine_distance_meters(
            float(payload.latitude),
            float(payload.longitude),
            float(site.latitude),
            float(site.longitude),
            site.radius_meters,
        )
        return True, distance.within_radius

    def check_in(self, current_user: CurrentUserContext, payload: AttendanceCheckRequest):
        schedule = self._load_schedule(payload.work_schedule_id)
        self._ensure_schedule_access(current_user, schedule)
        if schedule.schedule_status not in {"PUBLISHED", "APPROVED"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Schedule belum dipublish untuk presensi.",
            )
        if payload.method.startswith("gps") and (
            payload.latitude is None or payload.longitude is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Latitude dan longitude wajib untuk metode GPS.",
            )
        existing = self.repository.get_by_schedule_id(schedule.id)
        if existing is not None and existing.check_in_datetime is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Check-in untuk schedule ini sudah ada.",
            )
        shift = self.db.get(ShiftType, schedule.shift_type_id)
        check_in_at = utc_now()
        gps_flag, geofence_flag = self._geofence_flags(schedule, payload)
        tolerance = shift.tolerance_late_minutes if shift is not None else 0
        late_seconds = (
            check_in_at - self._as_utc(schedule.scheduled_start_datetime)
        ).total_seconds()
        minutes_late = max(0, int(late_seconds // 60) - tolerance)
        attendance_status = "LATE" if minutes_late > 0 else "PRESENT"

        record = existing or AttendanceRecord(
            employee_id=schedule.employee_id,
            work_schedule_id=schedule.id,
            client_site_id=schedule.client_site_id,
            site_post_id=schedule.site_post_id,
            attendance_date=schedule.scheduled_date,
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        record.check_in_datetime = check_in_at
        record.check_in_latitude = payload.latitude
        record.check_in_longitude = payload.longitude
        record.check_in_photo_path = payload.photo_path
        record.check_in_method = payload.method
        record.gps_valid_flag = gps_flag
        record.geofence_valid_flag = geofence_flag
        record.face_valid_flag = payload.photo_path is not None
        record.attendance_status = attendance_status
        record.minutes_late = minutes_late
        record.remarks = payload.remarks
        record.updated_by = current_user.user.id
        if existing is None:
            self.repository.create(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def check_out(self, current_user: CurrentUserContext, payload: AttendanceCheckRequest):
        schedule = self._load_schedule(payload.work_schedule_id)
        self._ensure_schedule_access(current_user, schedule)
        if schedule.schedule_status not in {"PUBLISHED", "APPROVED"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Schedule belum dipublish untuk presensi.",
            )
        if payload.method.startswith("gps") and (
            payload.latitude is None or payload.longitude is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Latitude dan longitude wajib untuk metode GPS.",
            )
        record = self.repository.get_by_schedule_id(schedule.id)
        if record is None or record.check_in_datetime is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check-in belum tercatat untuk schedule ini.",
            )
        if record.check_out_datetime is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Check-out untuk schedule ini sudah ada.",
            )
        shift = self.db.get(ShiftType, schedule.shift_type_id)
        check_out_at = utc_now()
        gps_flag, geofence_flag = self._geofence_flags(schedule, payload)
        working_minutes = max(
            0,
            int((check_out_at - self._as_utc(record.check_in_datetime)).total_seconds() // 60),
        )
        overtime_after = shift.overtime_after_minutes if shift is not None else 480
        overtime_minutes = max(0, working_minutes - overtime_after)

        record.check_out_datetime = check_out_at
        record.check_out_latitude = payload.latitude
        record.check_out_longitude = payload.longitude
        record.check_out_photo_path = payload.photo_path
        record.check_out_method = payload.method
        record.gps_valid_flag = record.gps_valid_flag or gps_flag
        record.geofence_valid_flag = record.geofence_valid_flag and geofence_flag
        record.face_valid_flag = record.face_valid_flag or payload.photo_path is not None
        record.working_minutes = working_minutes
        record.overtime_minutes = overtime_minutes
        record.attendance_status = "COMPLETED"
        if payload.remarks:
            record.remarks = payload.remarks
        record.updated_by = current_user.user.id
        self.db.commit()
        self.db.refresh(record)
        return record

    def create_manual_adjustment(
        self,
        current_user: CurrentUserContext,
        payload: AttendanceManualAdjustmentCreateRequest,
    ) -> AttendanceManualAdjustment:
        record = self.repository.get_record(payload.attendance_record_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record tidak ditemukan.",
            )
        allowed_record_ids = {item.id for item in self.list_records(current_user)}
        if record.id not in allowed_record_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Attendance record tidak berada dalam scope user.",
            )
        schedule = self._load_schedule(record.work_schedule_id)
        shift = self.db.get(ShiftType, schedule.shift_type_id)

        old_check_in = record.check_in_datetime
        old_check_out = record.check_out_datetime
        new_check_in = payload.new_check_in_datetime or old_check_in
        new_check_out = payload.new_check_out_datetime or old_check_out
        if payload.new_check_in_datetime is None and payload.new_check_out_datetime is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimal satu perubahan waktu attendance wajib dikirim.",
            )
        if new_check_in is not None and new_check_out is not None:
            if self._as_utc(new_check_out) < self._as_utc(new_check_in):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Check-out baru tidak boleh lebih awal dari check-in baru.",
                )

        if new_check_in is not None:
            late_seconds = (
                self._as_utc(new_check_in) - self._as_utc(schedule.scheduled_start_datetime)
            ).total_seconds()
            tolerance = shift.tolerance_late_minutes if shift is not None else 0
            record.minutes_late = max(0, int(late_seconds // 60) - tolerance)
            record.attendance_status = "LATE" if record.minutes_late > 0 else "PRESENT"
        if new_check_out is not None and new_check_in is not None:
            record.working_minutes = max(
                0,
                int((self._as_utc(new_check_out) - self._as_utc(new_check_in)).total_seconds() // 60),
            )
            overtime_after = shift.overtime_after_minutes if shift is not None else 480
            record.overtime_minutes = max(0, record.working_minutes - overtime_after)
            record.attendance_status = "COMPLETED"

        record.check_in_datetime = new_check_in
        record.check_out_datetime = new_check_out
        record.remarks = payload.reason
        record.updated_by = current_user.user.id
        adjustment = AttendanceManualAdjustment(
            attendance_record_id=record.id,
            old_check_in_datetime=old_check_in,
            new_check_in_datetime=new_check_in,
            old_check_out_datetime=old_check_out,
            new_check_out_datetime=new_check_out,
            reason=payload.reason,
            approved_by=current_user.user.id,
            created_by=current_user.user.id,
            created_at=utc_now(),
        )
        self.repository.create_manual_adjustment(adjustment)
        self.db.commit()
        self.db.refresh(adjustment)
        return adjustment

    def create_exception(
        self,
        current_user: CurrentUserContext,
        payload: AttendanceExceptionCreateRequest,
    ) -> AttendanceException:
        record = self.repository.get_record(payload.attendance_record_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record tidak ditemukan.",
            )
        allowed_record_ids = {item.id for item in self.list_records(current_user)}
        if record.id not in allowed_record_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Attendance exception tidak berada dalam scope user.",
            )
        item = AttendanceException(
            attendance_record_id=record.id,
            exception_type=payload.exception_type.strip().upper(),
            description=payload.description,
            resolution_status="OPEN",
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_exception(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def resolve_exception(
        self,
        current_user: CurrentUserContext,
        exception_id: int,
        payload: AttendanceExceptionResolveRequest,
    ) -> AttendanceException:
        item = self.repository.get_exception(exception_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance exception tidak ditemukan.",
            )
        allowed_exception_ids = {exception.id for exception in self.list_exceptions(current_user)}
        if item.id not in allowed_exception_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Attendance exception tidak berada dalam scope user.",
            )
        resolution_status = payload.resolution_status.strip().upper()
        if resolution_status not in {"RESOLVED", "REJECTED"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resolution status hanya boleh RESOLVED atau REJECTED.",
            )
        if item.resolution_status != "OPEN":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Attendance exception sudah diproses sebelumnya.",
            )
        item.resolution_status = resolution_status
        item.resolved_by = current_user.user.id
        item.resolved_at = utc_now()
        item.updated_by = current_user.user.id
        self.db.commit()
        self.db.refresh(item)
        return item
