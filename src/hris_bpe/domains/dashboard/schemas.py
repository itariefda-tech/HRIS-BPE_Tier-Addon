from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class DashboardGroupedCountRead(BaseModel):
    key: str
    total: int


class DashboardBranchCountRead(BaseModel):
    branch_id: int
    branch_name: str
    total: int


class DashboardSiteCountRead(BaseModel):
    client_site_id: int
    site_name: str
    total: int


class DashboardEmployeeReportRead(BaseModel):
    total_employees: int
    active_employees: int
    by_employee_status: list[DashboardGroupedCountRead]
    by_employment_status: list[DashboardGroupedCountRead]
    by_branch: list[DashboardBranchCountRead]


class DashboardDeploymentReportRead(BaseModel):
    total_deployments: int
    active_deployments: int
    by_status: list[DashboardGroupedCountRead]
    by_site: list[DashboardSiteCountRead]


class DashboardScheduleReportRead(BaseModel):
    date_from: date
    date_to: date
    total_schedules: int
    draft_schedules: int
    published_schedules: int
    approved_schedules: int
    by_status: list[DashboardGroupedCountRead]
    by_site: list[DashboardSiteCountRead]


class DashboardAttendanceReportRead(BaseModel):
    date_from: date
    date_to: date
    total_attendance: int
    present_attendance: int
    late_attendance: int
    completed_attendance: int
    gps_valid_total: int
    geofence_valid_total: int
    face_valid_total: int
    total_working_minutes: int
    total_overtime_minutes: int
    by_status: list[DashboardGroupedCountRead]
    by_site: list[DashboardSiteCountRead]
