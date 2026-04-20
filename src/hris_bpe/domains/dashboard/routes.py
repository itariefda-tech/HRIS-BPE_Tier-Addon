from datetime import date

from fastapi import APIRouter, Depends

from hris_bpe.common.dependencies import DbSession, require_permissions
from hris_bpe.common.responses import success_payload
from hris_bpe.domains.dashboard.schemas import (
    DashboardAttendanceReportRead,
    DashboardDeploymentReportRead,
    DashboardEmployeeReportRead,
    DashboardOpsSummaryRead,
    DashboardScheduleReportRead,
)
from hris_bpe.domains.dashboard.service import DashboardService


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/ops-summary")
def ops_summary(
    db: DbSession,
    current_user=Depends(require_permissions("dashboard.read")),
):
    service = DashboardService(db)
    data = DashboardOpsSummaryRead.model_validate(service.ops_summary(current_user))
    return success_payload(
        "Ringkasan operasional berhasil diambil.",
        data=data.model_dump(mode="json"),
    )


@router.get("/reports/employees")
def employee_report(
    db: DbSession,
    current_user=Depends(require_permissions("dashboard.read")),
):
    service = DashboardService(db)
    data = DashboardEmployeeReportRead.model_validate(service.employee_report(current_user))
    return success_payload(
        "Reporting employee berhasil diambil.",
        data=data.model_dump(mode="json"),
    )


@router.get("/reports/deployments")
def deployment_report(
    db: DbSession,
    current_user=Depends(require_permissions("dashboard.read")),
):
    service = DashboardService(db)
    data = DashboardDeploymentReportRead.model_validate(service.deployment_report(current_user))
    return success_payload(
        "Reporting deployment berhasil diambil.",
        data=data.model_dump(mode="json"),
    )


@router.get("/reports/schedules")
def schedule_report(
    db: DbSession,
    date_from: date | None = None,
    date_to: date | None = None,
    current_user=Depends(require_permissions("dashboard.read")),
):
    service = DashboardService(db)
    data = DashboardScheduleReportRead.model_validate(
        service.schedule_report(current_user, date_from=date_from, date_to=date_to)
    )
    return success_payload(
        "Reporting schedule berhasil diambil.",
        data=data.model_dump(mode="json"),
    )


@router.get("/reports/attendance")
def attendance_report(
    db: DbSession,
    date_from: date | None = None,
    date_to: date | None = None,
    current_user=Depends(require_permissions("dashboard.read")),
):
    service = DashboardService(db)
    data = DashboardAttendanceReportRead.model_validate(
        service.attendance_report(current_user, date_from=date_from, date_to=date_to)
    )
    return success_payload(
        "Reporting attendance berhasil diambil.",
        data=data.model_dump(mode="json"),
    )
