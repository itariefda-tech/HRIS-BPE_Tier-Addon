from fastapi import APIRouter, Depends, HTTPException, status

from hris_bpe.common.dependencies import CurrentUser, DbSession, require_permissions
from hris_bpe.common.responses import success_payload
from hris_bpe.domains.attendance.schemas import (
    AttendanceCheckRequest,
    AttendanceExceptionCreateRequest,
    AttendanceExceptionRead,
    AttendanceExceptionResolveRequest,
    AttendanceManualAdjustmentCreateRequest,
    AttendanceManualAdjustmentRead,
    AttendanceQrConsumeRequest,
    AttendanceQrSessionCreateRequest,
    AttendanceQrSessionIssuedRead,
    AttendanceQrSessionRead,
    AttendanceRead,
)
from hris_bpe.domains.attendance.service import AttendanceService


router = APIRouter(prefix="/attendance", tags=["attendance"])


def _ensure_attendance_write_access(current_user: CurrentUser) -> None:
    if "attendance.self_service" not in current_user.permission_codes and "attendance.manage" not in current_user.permission_codes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Izin attendance tidak cukup.",
        )


@router.get("/records")
def list_records(
    db: DbSession,
    current_user=Depends(require_permissions("attendance.read")),
):
    service = AttendanceService(db)
    items = [
        AttendanceRead.model_validate(item).model_dump(mode="json")
        for item in service.list_records(current_user)
    ]
    return success_payload("Daftar attendance berhasil diambil.", data=items, meta={"total": len(items)})


@router.get("/records/{attendance_record_id}")
def get_record(
    attendance_record_id: int,
    db: DbSession,
    current_user=Depends(require_permissions("attendance.read")),
):
    service = AttendanceService(db)
    item = service.get_record(current_user, attendance_record_id)
    return success_payload(
        "Detail attendance berhasil diambil.",
        data=AttendanceRead.model_validate(item).model_dump(mode="json"),
    )


@router.post("/check-in")
def check_in(
    payload: AttendanceCheckRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    _ensure_attendance_write_access(current_user)
    service = AttendanceService(db)
    item = service.check_in(current_user, payload)
    return success_payload("Check-in berhasil dicatat.", data=AttendanceRead.model_validate(item).model_dump(mode="json"))


@router.post("/check-out")
def check_out(
    payload: AttendanceCheckRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    _ensure_attendance_write_access(current_user)
    service = AttendanceService(db)
    item = service.check_out(current_user, payload)
    return success_payload("Check-out berhasil dicatat.", data=AttendanceRead.model_validate(item).model_dump(mode="json"))


@router.post("/qr-sessions")
def create_qr_session(
    payload: AttendanceQrSessionCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("attendance.manage")),
):
    service = AttendanceService(db)
    item, qr_token = service.create_qr_session(current_user, payload)
    session_payload = AttendanceQrSessionRead.model_validate(item).model_dump(mode="json")
    response_payload = AttendanceQrSessionIssuedRead(
        **session_payload,
        qr_token=qr_token,
    )
    return success_payload(
        "QR attendance session berhasil dibuat.",
        data=response_payload.model_dump(mode="json"),
    )


@router.post("/check-in/qr")
def check_in_by_qr(
    payload: AttendanceQrConsumeRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    _ensure_attendance_write_access(current_user)
    service = AttendanceService(db)
    item = service.check_in_by_qr(current_user, payload)
    return success_payload(
        "Check-in QR berhasil dicatat.",
        data=AttendanceRead.model_validate(item).model_dump(mode="json"),
    )


@router.post("/check-out/qr")
def check_out_by_qr(
    payload: AttendanceQrConsumeRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    _ensure_attendance_write_access(current_user)
    service = AttendanceService(db)
    item = service.check_out_by_qr(current_user, payload)
    return success_payload(
        "Check-out QR berhasil dicatat.",
        data=AttendanceRead.model_validate(item).model_dump(mode="json"),
    )


@router.get("/manual-adjustments")
def list_manual_adjustments(
    db: DbSession,
    current_user=Depends(require_permissions("attendance.read")),
):
    service = AttendanceService(db)
    items = [
        AttendanceManualAdjustmentRead.model_validate(item).model_dump(mode="json")
        for item in service.list_manual_adjustments(current_user)
    ]
    return success_payload("Daftar manual adjustment berhasil diambil.", data=items, meta={"total": len(items)})


@router.get("/exceptions")
def list_exceptions(
    db: DbSession,
    current_user=Depends(require_permissions("attendance.read")),
):
    service = AttendanceService(db)
    items = [
        AttendanceExceptionRead.model_validate(item).model_dump(mode="json")
        for item in service.list_exceptions(current_user)
    ]
    return success_payload(
        "Daftar attendance exception berhasil diambil.",
        data=items,
        meta={"total": len(items)},
    )


@router.post("/exceptions")
def create_exception(
    payload: AttendanceExceptionCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    _ensure_attendance_write_access(current_user)
    service = AttendanceService(db)
    item = service.create_exception(current_user, payload)
    return success_payload(
        "Attendance exception berhasil dibuat.",
        data=AttendanceExceptionRead.model_validate(item).model_dump(mode="json"),
    )


@router.post("/exceptions/{exception_id}/resolve")
def resolve_exception(
    exception_id: int,
    payload: AttendanceExceptionResolveRequest,
    db: DbSession,
    current_user=Depends(require_permissions("attendance.manage")),
):
    service = AttendanceService(db)
    item = service.resolve_exception(current_user, exception_id, payload)
    return success_payload(
        "Attendance exception berhasil diproses.",
        data=AttendanceExceptionRead.model_validate(item).model_dump(mode="json"),
    )


@router.post("/manual-adjustments")
def create_manual_adjustment(
    payload: AttendanceManualAdjustmentCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("attendance.manage")),
):
    service = AttendanceService(db)
    item = service.create_manual_adjustment(current_user, payload)
    return success_payload(
        "Manual adjustment attendance berhasil dibuat.",
        data=AttendanceManualAdjustmentRead.model_validate(item).model_dump(mode="json"),
    )
