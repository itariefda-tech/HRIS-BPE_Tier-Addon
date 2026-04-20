from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from hris_bpe.domains.attendance.models import (
    AttendanceException,
    AttendanceManualAdjustment,
    AttendanceQrSession,
    AttendanceRecord,
)


class AttendanceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_schedule_id(self, work_schedule_id: int) -> AttendanceRecord | None:
        return self.db.execute(
            select(AttendanceRecord).where(AttendanceRecord.work_schedule_id == work_schedule_id)
        ).scalar_one_or_none()

    def list_records(self) -> list[AttendanceRecord]:
        return list(
            self.db.execute(
                select(AttendanceRecord).order_by(AttendanceRecord.attendance_date.desc())
            ).scalars()
        )

    def create(self, item: AttendanceRecord) -> AttendanceRecord:
        self.db.add(item)
        self.db.flush()
        return item

    def list_manual_adjustments(self) -> list[AttendanceManualAdjustment]:
        return list(
            self.db.execute(
                select(AttendanceManualAdjustment).order_by(
                    AttendanceManualAdjustment.created_at.desc()
                )
            ).scalars()
        )

    def create_manual_adjustment(
        self, item: AttendanceManualAdjustment
    ) -> AttendanceManualAdjustment:
        self.db.add(item)
        self.db.flush()
        return item

    def get_record(self, attendance_record_id: int) -> AttendanceRecord | None:
        return self.db.get(AttendanceRecord, attendance_record_id)

    def list_exceptions(self) -> list[AttendanceException]:
        return list(
            self.db.execute(
                select(AttendanceException).order_by(AttendanceException.created_at.desc())
            ).scalars()
        )

    def create_exception(self, item: AttendanceException) -> AttendanceException:
        self.db.add(item)
        self.db.flush()
        return item

    def get_exception(self, exception_id: int) -> AttendanceException | None:
        return self.db.get(AttendanceException, exception_id)

    def create_qr_session(self, item: AttendanceQrSession) -> AttendanceQrSession:
        self.db.add(item)
        self.db.flush()
        return item

    def get_qr_session_by_token_hash(self, token_hash: str) -> AttendanceQrSession | None:
        return self.db.execute(
            select(AttendanceQrSession).where(AttendanceQrSession.token_hash == token_hash)
        ).scalar_one_or_none()
