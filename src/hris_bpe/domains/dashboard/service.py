from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from hris_bpe.common.helpers import today_local
from hris_bpe.common.scope import resolve_company_scope_ids
from hris_bpe.common.dependencies import CurrentUserContext
from hris_bpe.domains.attendance.models import AttendanceRecord
from hris_bpe.domains.client_contract.models import Client
from hris_bpe.domains.master_hr.models import Employee
from hris_bpe.domains.site_operations.models import ClientSite
from hris_bpe.domains.workforce_operations.models import EmployeeDeployment, WorkSchedule


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def ops_summary(self, current_user: CurrentUserContext) -> dict[str, int]:
        today = today_local()
        allowed_company_ids = resolve_company_scope_ids(current_user)
        employee_stmt = select(func.count()).select_from(Employee)
        site_stmt = select(func.count()).select_from(ClientSite)
        deployment_stmt = select(func.count()).select_from(EmployeeDeployment).where(
            EmployeeDeployment.deployment_status == "ACTIVE"
        )
        schedule_stmt = select(func.count()).select_from(WorkSchedule).where(
            WorkSchedule.scheduled_date == today
        )
        attendance_stmt = select(func.count()).select_from(AttendanceRecord).where(
            AttendanceRecord.attendance_date == today
        )
        client_stmt = select(func.count()).select_from(Client)

        if allowed_company_ids:
            employee_stmt = employee_stmt.where(Employee.company_id.in_(allowed_company_ids))
            client_stmt = client_stmt.where(Client.company_id.in_(allowed_company_ids))
            site_stmt = site_stmt.join(Client, Client.id == ClientSite.client_id).where(
                Client.company_id.in_(allowed_company_ids)
            )
            deployment_stmt = deployment_stmt.join(
                Employee, Employee.id == EmployeeDeployment.employee_id
            ).where(Employee.company_id.in_(allowed_company_ids))
            schedule_stmt = schedule_stmt.join(
                Employee, Employee.id == WorkSchedule.employee_id
            ).where(Employee.company_id.in_(allowed_company_ids))
            attendance_stmt = attendance_stmt.join(
                Employee, Employee.id == AttendanceRecord.employee_id
            ).where(Employee.company_id.in_(allowed_company_ids))

        if current_user.site_scope_ids:
            site_stmt = site_stmt.where(ClientSite.id.in_(current_user.site_scope_ids))
            deployment_stmt = deployment_stmt.where(
                EmployeeDeployment.client_site_id.in_(current_user.site_scope_ids)
            )
            schedule_stmt = schedule_stmt.where(
                WorkSchedule.client_site_id.in_(current_user.site_scope_ids)
            )
            attendance_stmt = attendance_stmt.where(
                AttendanceRecord.client_site_id.in_(current_user.site_scope_ids)
            )
        if current_user.branch_scope_ids:
            employee_stmt = employee_stmt.where(Employee.branch_id.in_(current_user.branch_scope_ids))
        if current_user.user.employee_id is not None and "dashboard.read" in current_user.permission_codes and "attendance.manage" not in current_user.permission_codes:
            employee_stmt = employee_stmt.where(Employee.id == current_user.user.employee_id)
            deployment_stmt = deployment_stmt.where(
                EmployeeDeployment.employee_id == current_user.user.employee_id
            )
            schedule_stmt = schedule_stmt.where(
                WorkSchedule.employee_id == current_user.user.employee_id
            )
            attendance_stmt = attendance_stmt.where(
                AttendanceRecord.employee_id == current_user.user.employee_id
            )

        employees_total = self.db.execute(employee_stmt).scalar_one()
        clients_total = self.db.execute(client_stmt).scalar_one()
        sites_total = self.db.execute(site_stmt).scalar_one()
        active_deployments = self.db.execute(deployment_stmt).scalar_one()
        schedules_today = self.db.execute(schedule_stmt).scalar_one()
        attendance_today = self.db.execute(attendance_stmt).scalar_one()
        return {
            "employees_total": int(employees_total or 0),
            "clients_total": int(clients_total or 0),
            "sites_total": int(sites_total or 0),
            "active_deployments": int(active_deployments or 0),
            "schedules_today": int(schedules_today or 0),
            "attendance_today": int(attendance_today or 0),
        }
