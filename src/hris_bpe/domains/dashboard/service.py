from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from hris_bpe.common.dependencies import CurrentUserContext
from hris_bpe.common.helpers import today_local
from hris_bpe.common.scope import resolve_company_scope_ids
from hris_bpe.domains.attendance.models import AttendanceRecord
from hris_bpe.domains.client_contract.models import Client
from hris_bpe.domains.master_hr.models import Employee
from hris_bpe.domains.organization.models import Branch
from hris_bpe.domains.site_operations.models import ClientSite
from hris_bpe.domains.workforce_operations.models import EmployeeDeployment, WorkSchedule


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _is_self_dashboard_scope(current_user: CurrentUserContext) -> bool:
        return (
            current_user.user.employee_id is not None
            and "attendance.manage" not in current_user.permission_codes
        )

    def _allowed_employee_ids_stmt(self, current_user: CurrentUserContext):
        stmt = select(Employee.id).distinct()
        allowed_company_ids = resolve_company_scope_ids(current_user)
        if allowed_company_ids:
            stmt = stmt.where(Employee.company_id.in_(allowed_company_ids))
        if current_user.branch_scope_ids:
            stmt = stmt.where(Employee.branch_id.in_(current_user.branch_scope_ids))
        if current_user.site_scope_ids:
            stmt = stmt.join(
                EmployeeDeployment,
                EmployeeDeployment.employee_id == Employee.id,
            ).where(EmployeeDeployment.client_site_id.in_(current_user.site_scope_ids))
        if self._is_self_dashboard_scope(current_user):
            stmt = stmt.where(Employee.id == current_user.user.employee_id)
        return stmt

    def _allowed_client_ids_stmt(self, current_user: CurrentUserContext):
        stmt = select(Client.id).distinct()
        allowed_company_ids = resolve_company_scope_ids(current_user)
        if allowed_company_ids:
            stmt = stmt.where(Client.company_id.in_(allowed_company_ids))
        if current_user.site_scope_ids:
            stmt = stmt.join(ClientSite, ClientSite.client_id == Client.id).where(
                ClientSite.id.in_(current_user.site_scope_ids)
            )
        elif current_user.branch_scope_ids or self._is_self_dashboard_scope(current_user):
            stmt = stmt.join(
                EmployeeDeployment,
                EmployeeDeployment.client_id == Client.id,
            ).where(EmployeeDeployment.employee_id.in_(self._allowed_employee_ids_stmt(current_user)))
        return stmt

    def _allowed_site_ids_stmt(self, current_user: CurrentUserContext):
        stmt = select(ClientSite.id).distinct().join(Client, Client.id == ClientSite.client_id)
        allowed_company_ids = resolve_company_scope_ids(current_user)
        if allowed_company_ids:
            stmt = stmt.where(Client.company_id.in_(allowed_company_ids))
        if current_user.site_scope_ids:
            stmt = stmt.where(ClientSite.id.in_(current_user.site_scope_ids))
        elif current_user.branch_scope_ids or self._is_self_dashboard_scope(current_user):
            stmt = stmt.join(
                EmployeeDeployment,
                EmployeeDeployment.client_site_id == ClientSite.id,
            ).where(EmployeeDeployment.employee_id.in_(self._allowed_employee_ids_stmt(current_user)))
        return stmt

    def _operational_scope_conditions(
        self,
        current_user: CurrentUserContext,
        *,
        employee_id_column,
        site_id_column,
    ) -> tuple:
        conditions = [employee_id_column.in_(self._allowed_employee_ids_stmt(current_user))]
        if current_user.site_scope_ids:
            conditions.append(site_id_column.in_(current_user.site_scope_ids))
        return tuple(conditions)

    @staticmethod
    def _normalize_date_range(
        date_from: date | None,
        date_to: date | None,
    ) -> tuple[date, date]:
        normalized_from = date_from or today_local()
        normalized_to = date_to or normalized_from
        if normalized_from > normalized_to:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="date_from tidak boleh lebih besar dari date_to.",
            )
        return normalized_from, normalized_to

    @staticmethod
    def _grouped_count_payload(rows) -> list[dict[str, int | str]]:
        return [{"key": str(row.key), "total": int(row.total or 0)} for row in rows]

    @staticmethod
    def _site_count_payload(rows) -> list[dict[str, int | str]]:
        return [
            {
                "client_site_id": int(row.client_site_id),
                "site_name": row.site_name,
                "total": int(row.total or 0),
            }
            for row in rows
        ]

    def ops_summary(self, current_user: CurrentUserContext) -> dict[str, int]:
        today = today_local()
        employee_stmt = select(func.count()).select_from(Employee).where(
            Employee.id.in_(self._allowed_employee_ids_stmt(current_user))
        )
        client_stmt = select(func.count()).select_from(Client).where(
            Client.id.in_(self._allowed_client_ids_stmt(current_user))
        )
        site_stmt = select(func.count()).select_from(ClientSite).where(
            ClientSite.id.in_(self._allowed_site_ids_stmt(current_user))
        )
        deployment_stmt = (
            select(func.count())
            .select_from(EmployeeDeployment)
            .where(EmployeeDeployment.deployment_status == "ACTIVE")
            .where(
                *self._operational_scope_conditions(
                    current_user,
                    employee_id_column=EmployeeDeployment.employee_id,
                    site_id_column=EmployeeDeployment.client_site_id,
                )
            )
        )
        schedule_stmt = (
            select(func.count())
            .select_from(WorkSchedule)
            .where(WorkSchedule.scheduled_date == today)
            .where(
                *self._operational_scope_conditions(
                    current_user,
                    employee_id_column=WorkSchedule.employee_id,
                    site_id_column=WorkSchedule.client_site_id,
                )
            )
        )
        attendance_stmt = (
            select(func.count())
            .select_from(AttendanceRecord)
            .where(AttendanceRecord.attendance_date == today)
            .where(
                *self._operational_scope_conditions(
                    current_user,
                    employee_id_column=AttendanceRecord.employee_id,
                    site_id_column=AttendanceRecord.client_site_id,
                )
            )
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

    def employee_report(self, current_user: CurrentUserContext) -> dict:
        employee_scope = Employee.id.in_(self._allowed_employee_ids_stmt(current_user))
        total_employees = self.db.execute(
            select(func.count()).select_from(Employee).where(employee_scope)
        ).scalar_one()
        active_employees = self.db.execute(
            select(func.count())
            .select_from(Employee)
            .where(employee_scope, Employee.employee_status == "ACTIVE")
        ).scalar_one()

        employee_status_key = func.coalesce(Employee.employee_status, "UNSET").label("key")
        employment_status_key = func.coalesce(Employee.employment_status, "UNSET").label("key")
        by_employee_status_rows = self.db.execute(
            select(employee_status_key, func.count(Employee.id).label("total"))
            .where(employee_scope)
            .group_by(employee_status_key)
            .order_by(func.count(Employee.id).desc(), employee_status_key.asc())
        ).all()
        by_employment_status_rows = self.db.execute(
            select(employment_status_key, func.count(Employee.id).label("total"))
            .where(employee_scope)
            .group_by(employment_status_key)
            .order_by(func.count(Employee.id).desc(), employment_status_key.asc())
        ).all()
        by_branch_rows = self.db.execute(
            select(
                Branch.id.label("branch_id"),
                Branch.name.label("branch_name"),
                func.count(Employee.id).label("total"),
            )
            .join(Employee, Employee.branch_id == Branch.id)
            .where(employee_scope)
            .group_by(Branch.id, Branch.name)
            .order_by(func.count(Employee.id).desc(), Branch.name.asc())
        ).all()

        return {
            "total_employees": int(total_employees or 0),
            "active_employees": int(active_employees or 0),
            "by_employee_status": self._grouped_count_payload(by_employee_status_rows),
            "by_employment_status": self._grouped_count_payload(by_employment_status_rows),
            "by_branch": [
                {
                    "branch_id": int(row.branch_id),
                    "branch_name": row.branch_name,
                    "total": int(row.total or 0),
                }
                for row in by_branch_rows
            ],
        }

    def deployment_report(self, current_user: CurrentUserContext) -> dict:
        scope_conditions = self._operational_scope_conditions(
            current_user,
            employee_id_column=EmployeeDeployment.employee_id,
            site_id_column=EmployeeDeployment.client_site_id,
        )
        total_deployments = self.db.execute(
            select(func.count()).select_from(EmployeeDeployment).where(*scope_conditions)
        ).scalar_one()
        active_deployments = self.db.execute(
            select(func.count())
            .select_from(EmployeeDeployment)
            .where(*scope_conditions, EmployeeDeployment.deployment_status == "ACTIVE")
        ).scalar_one()

        status_key = func.coalesce(EmployeeDeployment.deployment_status, "UNSET").label("key")
        by_status_rows = self.db.execute(
            select(status_key, func.count(EmployeeDeployment.id).label("total"))
            .where(*scope_conditions)
            .group_by(status_key)
            .order_by(func.count(EmployeeDeployment.id).desc(), status_key.asc())
        ).all()
        by_site_rows = self.db.execute(
            select(
                ClientSite.id.label("client_site_id"),
                ClientSite.name.label("site_name"),
                func.count(EmployeeDeployment.id).label("total"),
            )
            .join(ClientSite, ClientSite.id == EmployeeDeployment.client_site_id)
            .where(*scope_conditions)
            .group_by(ClientSite.id, ClientSite.name)
            .order_by(func.count(EmployeeDeployment.id).desc(), ClientSite.name.asc())
        ).all()
        return {
            "total_deployments": int(total_deployments or 0),
            "active_deployments": int(active_deployments or 0),
            "by_status": self._grouped_count_payload(by_status_rows),
            "by_site": self._site_count_payload(by_site_rows),
        }

    def schedule_report(
        self,
        current_user: CurrentUserContext,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict:
        normalized_from, normalized_to = self._normalize_date_range(date_from, date_to)
        scope_conditions = self._operational_scope_conditions(
            current_user,
            employee_id_column=WorkSchedule.employee_id,
            site_id_column=WorkSchedule.client_site_id,
        )
        date_conditions = [
            WorkSchedule.scheduled_date >= normalized_from,
            WorkSchedule.scheduled_date <= normalized_to,
        ]
        total_schedules = self.db.execute(
            select(func.count())
            .select_from(WorkSchedule)
            .where(*scope_conditions, *date_conditions)
        ).scalar_one()

        status_key = func.coalesce(WorkSchedule.schedule_status, "UNSET").label("key")
        by_status_rows = self.db.execute(
            select(status_key, func.count(WorkSchedule.id).label("total"))
            .where(*scope_conditions, *date_conditions)
            .group_by(status_key)
            .order_by(func.count(WorkSchedule.id).desc(), status_key.asc())
        ).all()
        status_totals = {str(row.key): int(row.total or 0) for row in by_status_rows}
        by_site_rows = self.db.execute(
            select(
                ClientSite.id.label("client_site_id"),
                ClientSite.name.label("site_name"),
                func.count(WorkSchedule.id).label("total"),
            )
            .join(ClientSite, ClientSite.id == WorkSchedule.client_site_id)
            .where(*scope_conditions, *date_conditions)
            .group_by(ClientSite.id, ClientSite.name)
            .order_by(func.count(WorkSchedule.id).desc(), ClientSite.name.asc())
        ).all()

        return {
            "date_from": normalized_from,
            "date_to": normalized_to,
            "total_schedules": int(total_schedules or 0),
            "draft_schedules": int(status_totals.get("DRAFT", 0)),
            "published_schedules": int(status_totals.get("PUBLISHED", 0)),
            "approved_schedules": int(status_totals.get("APPROVED", 0)),
            "by_status": self._grouped_count_payload(by_status_rows),
            "by_site": self._site_count_payload(by_site_rows),
        }

    def attendance_report(
        self,
        current_user: CurrentUserContext,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict:
        normalized_from, normalized_to = self._normalize_date_range(date_from, date_to)
        scope_conditions = self._operational_scope_conditions(
            current_user,
            employee_id_column=AttendanceRecord.employee_id,
            site_id_column=AttendanceRecord.client_site_id,
        )
        date_conditions = [
            AttendanceRecord.attendance_date >= normalized_from,
            AttendanceRecord.attendance_date <= normalized_to,
        ]
        aggregate_row = self.db.execute(
            select(
                func.count(AttendanceRecord.id).label("total_attendance"),
                func.coalesce(func.sum(AttendanceRecord.working_minutes), 0).label(
                    "total_working_minutes"
                ),
                func.coalesce(func.sum(AttendanceRecord.overtime_minutes), 0).label(
                    "total_overtime_minutes"
                ),
                func.coalesce(
                    func.sum(
                        case((AttendanceRecord.gps_valid_flag.is_(True), 1), else_=0)
                    ),
                    0,
                ).label("gps_valid_total"),
                func.coalesce(
                    func.sum(
                        case((AttendanceRecord.geofence_valid_flag.is_(True), 1), else_=0)
                    ),
                    0,
                ).label("geofence_valid_total"),
                func.coalesce(
                    func.sum(
                        case((AttendanceRecord.face_valid_flag.is_(True), 1), else_=0)
                    ),
                    0,
                ).label("face_valid_total"),
            )
            .select_from(AttendanceRecord)
            .where(*scope_conditions, *date_conditions)
        ).one()

        status_key = func.coalesce(AttendanceRecord.attendance_status, "UNSET").label("key")
        by_status_rows = self.db.execute(
            select(status_key, func.count(AttendanceRecord.id).label("total"))
            .where(*scope_conditions, *date_conditions)
            .group_by(status_key)
            .order_by(func.count(AttendanceRecord.id).desc(), status_key.asc())
        ).all()
        status_totals = {str(row.key): int(row.total or 0) for row in by_status_rows}
        by_site_rows = self.db.execute(
            select(
                ClientSite.id.label("client_site_id"),
                ClientSite.name.label("site_name"),
                func.count(AttendanceRecord.id).label("total"),
            )
            .join(ClientSite, ClientSite.id == AttendanceRecord.client_site_id)
            .where(*scope_conditions, *date_conditions)
            .group_by(ClientSite.id, ClientSite.name)
            .order_by(func.count(AttendanceRecord.id).desc(), ClientSite.name.asc())
        ).all()

        return {
            "date_from": normalized_from,
            "date_to": normalized_to,
            "total_attendance": int(aggregate_row.total_attendance or 0),
            "present_attendance": int(status_totals.get("PRESENT", 0)),
            "late_attendance": int(status_totals.get("LATE", 0)),
            "completed_attendance": int(status_totals.get("COMPLETED", 0)),
            "gps_valid_total": int(aggregate_row.gps_valid_total or 0),
            "geofence_valid_total": int(aggregate_row.geofence_valid_total or 0),
            "face_valid_total": int(aggregate_row.face_valid_total or 0),
            "total_working_minutes": int(aggregate_row.total_working_minutes or 0),
            "total_overtime_minutes": int(aggregate_row.total_overtime_minutes or 0),
            "by_status": self._grouped_count_payload(by_status_rows),
            "by_site": self._site_count_payload(by_site_rows),
        }
