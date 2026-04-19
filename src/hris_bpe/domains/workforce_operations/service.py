from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hris_bpe.common.dependencies import CurrentUserContext
from hris_bpe.common.helpers import utc_now
from hris_bpe.common.scope import ensure_company_access, filter_items_by_company_scope, has_unscoped_permission
from hris_bpe.domains.client_contract.models import Client, ClientContract
from hris_bpe.domains.master_hr.models import Employee
from hris_bpe.domains.site_operations.models import ClientSite, SitePost
from hris_bpe.domains.workforce_operations.models import (
    DeploymentHistory,
    EmployeeDeployment,
    ShiftType,
    WorkSchedule,
)
from hris_bpe.domains.workforce_operations.repository import WorkforceOperationsRepository
from hris_bpe.domains.workforce_operations.schemas import (
    BulkScheduleGenerateRequest,
    EndDeploymentRequest,
    EmployeeDeploymentCreateRequest,
    ShiftTypeCreateRequest,
    WorkScheduleCreateRequest,
)


class WorkforceOperationsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = WorkforceOperationsRepository(db)

    def _filter_deployments(
        self, current_user: CurrentUserContext, items: list[EmployeeDeployment]
    ) -> list[EmployeeDeployment]:
        client_company_map = {
            client.id: client.company_id for client in self.db.query(Client).all()
        }
        items = filter_items_by_company_scope(
            current_user,
            items,
            lambda item: client_company_map.get(item.client_id),
        )
        if has_unscoped_permission(current_user, "deployments.manage"):
            return items
        if current_user.site_scope_ids:
            items = [item for item in items if item.client_site_id in current_user.site_scope_ids]
        if current_user.branch_scope_ids:
            employee_map = {employee.id: employee.branch_id for employee in self.db.query(Employee).all()}
            items = [
                item
                for item in items
                if employee_map.get(item.employee_id) in current_user.branch_scope_ids
            ]
        if current_user.user.employee_id is not None and "deployments.manage" not in current_user.permission_codes:
            items = [item for item in items if item.employee_id == current_user.user.employee_id]
        return items

    def list_deployments(self, current_user: CurrentUserContext):
        return self._filter_deployments(current_user, self.repository.list_deployments())

    def list_deployment_histories(self, current_user: CurrentUserContext):
        allowed_deployment_ids = {item.id for item in self.list_deployments(current_user)}
        return [
            item
            for item in self.repository.list_deployment_histories()
            if item.employee_deployment_id in allowed_deployment_ids
        ]

    def create_deployment(
        self,
        current_user: CurrentUserContext,
        payload: EmployeeDeploymentCreateRequest,
        created_by: int | None,
    ):
        employee = self.db.get(Employee, payload.employee_id)
        client = self.db.get(Client, payload.client_id)
        contract = self.db.get(ClientContract, payload.client_contract_id)
        site = self.db.get(ClientSite, payload.client_site_id)
        post = self.db.get(SitePost, payload.site_post_id) if payload.site_post_id else None
        if employee is None or client is None or contract is None or site is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referensi deployment tidak lengkap atau tidak ditemukan.",
            )
        ensure_company_access(
            current_user,
            employee.company_id,
            detail="Employee deployment tidak berada dalam scope company user.",
        )
        ensure_company_access(
            current_user,
            client.company_id,
            detail="Client deployment tidak berada dalam scope company user.",
        )
        if current_user.site_scope_ids and payload.client_site_id not in current_user.site_scope_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Site deployment tidak berada dalam scope user.",
            )
        if current_user.branch_scope_ids:
            if employee.branch_id not in current_user.branch_scope_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Employee deployment tidak berada dalam scope branch user.",
                )
        if contract.client_id != client.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client contract tidak cocok dengan client deployment.",
            )
        if site.client_id != client.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client site tidak cocok dengan client deployment.",
            )
        if post is not None and post.client_site_id != site.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Site post tidak cocok dengan client site deployment.",
            )
        item = EmployeeDeployment(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_deployment(item)
        self.repository.create_deployment_history(
            DeploymentHistory(
                employee_deployment_id=item.id,
                action_type="CREATE",
                old_client_site_id=None,
                new_client_site_id=item.client_site_id,
                old_site_post_id=None,
                new_site_post_id=item.site_post_id,
                action_date=item.start_date,
                remarks=item.notes,
                created_by=created_by,
                created_at=utc_now(),
            )
        )
        self.db.commit()
        self.db.refresh(item)
        return item

    @staticmethod
    def _normalize_schedule_status_for_creation(schedule_status: str) -> str:
        normalized = schedule_status.strip().upper()
        if normalized not in {"DRAFT", "PUBLISHED"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status schedule saat create/generate hanya boleh DRAFT atau PUBLISHED.",
            )
        return normalized

    def list_shift_types(self, current_user: CurrentUserContext):
        return filter_items_by_company_scope(
            current_user,
            self.repository.list_shift_types(),
            lambda item: item.company_id,
        )

    def create_shift_type(self, current_user: CurrentUserContext, payload: ShiftTypeCreateRequest):
        ensure_company_access(
            current_user,
            payload.company_id,
            detail="Shift type tidak berada dalam scope company user.",
        )
        item = ShiftType(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_shift_type(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_work_schedules(self, current_user: CurrentUserContext):
        employee_company_map = {
            employee.id: employee.company_id for employee in self.db.query(Employee).all()
        }
        items = filter_items_by_company_scope(
            current_user,
            self.repository.list_work_schedules(),
            lambda item: employee_company_map.get(item.employee_id),
        )
        if has_unscoped_permission(current_user, "schedules.manage"):
            return items
        if current_user.site_scope_ids:
            items = [item for item in items if item.client_site_id in current_user.site_scope_ids]
        if current_user.branch_scope_ids:
            employee_map = {employee.id: employee.branch_id for employee in self.db.query(Employee).all()}
            items = [
                item
                for item in items
                if employee_map.get(item.employee_id) in current_user.branch_scope_ids
            ]
        if current_user.user.employee_id is not None and "schedules.manage" not in current_user.permission_codes:
            items = [item for item in items if item.employee_id == current_user.user.employee_id]
        return items

    def create_work_schedule(
        self,
        current_user: CurrentUserContext,
        payload: WorkScheduleCreateRequest,
        generated_by: int | None,
        approved_by: int | None,
    ):
        deployment = self.repository.get_deployment(payload.employee_deployment_id)
        if deployment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment tidak ditemukan.",
            )
        allowed_deployment_ids = {item.id for item in self.list_deployments(current_user)}
        if deployment.id not in allowed_deployment_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Deployment untuk schedule tidak berada dalam scope user.",
            )
        schedule_status = self._normalize_schedule_status_for_creation(payload.schedule_status)
        shift_type = self.repository.get_shift_type(payload.shift_type_id)
        if shift_type is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shift type tidak ditemukan.",
            )
        ensure_company_access(
            current_user,
            shift_type.company_id,
            detail="Shift type schedule tidak berada dalam scope company user.",
        )

        start_dt = payload.scheduled_start_datetime
        end_dt = payload.scheduled_end_datetime
        if start_dt is None:
            start_dt = datetime.combine(
                payload.scheduled_date,
                shift_type.start_time,
                tzinfo=timezone.utc,
            )
        if end_dt is None:
            end_date = payload.scheduled_date
            if shift_type.cross_day_flag:
                end_date = end_date + timedelta(days=1)
            end_dt = datetime.combine(end_date, shift_type.end_time, tzinfo=timezone.utc)

        item = WorkSchedule(
            employee_id=deployment.employee_id,
            employee_deployment_id=deployment.id,
            client_site_id=deployment.client_site_id,
            site_post_id=deployment.site_post_id,
            shift_type_id=shift_type.id,
            scheduled_date=payload.scheduled_date,
            scheduled_start_datetime=start_dt,
            scheduled_end_datetime=end_dt,
            schedule_status=schedule_status,
            replacement_for_schedule_id=payload.replacement_for_schedule_id,
            generated_by=generated_by,
            approved_by=approved_by if schedule_status == "APPROVED" else None,
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_work_schedule(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def generate_bulk_schedules(
        self,
        current_user: CurrentUserContext,
        payload: BulkScheduleGenerateRequest,
    ) -> list[WorkSchedule]:
        shift_type = self.repository.get_shift_type(payload.shift_type_id)
        if shift_type is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shift type tidak ditemukan.",
            )
        created_items: list[WorkSchedule] = []
        deployment_map = {
            item.id: item for item in self.list_deployments(current_user)
        }
        target_date = payload.date_from
        while target_date <= payload.date_to:
            for deployment_id in payload.employee_deployment_ids:
                deployment = deployment_map.get(deployment_id)
                if deployment is None:
                    continue
                if deployment.deployment_status != "ACTIVE":
                    continue
                if deployment.start_date > target_date:
                    continue
                if deployment.end_date is not None and deployment.end_date < target_date:
                    continue
                existing = self.repository.find_schedule_for_deployment_on_date(
                    deployment.id, target_date
                )
                if existing is not None:
                    continue
                request = WorkScheduleCreateRequest(
                    employee_deployment_id=deployment.id,
                    shift_type_id=payload.shift_type_id,
                    scheduled_date=target_date,
                    schedule_status=payload.schedule_status,
                )
                created_items.append(
                    self.create_work_schedule(
                        current_user=current_user,
                        payload=request,
                        generated_by=current_user.user.id,
                        approved_by=None,
                    )
                )
            target_date += timedelta(days=1)
        return created_items

    def publish_work_schedule(
        self, current_user: CurrentUserContext, schedule_id: int
    ) -> WorkSchedule:
        schedule = self.repository.get_work_schedule(schedule_id)
        if schedule is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Work schedule tidak ditemukan.",
            )
        allowed_schedule_ids = {item.id for item in self.list_work_schedules(current_user)}
        if schedule.id not in allowed_schedule_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Work schedule tidak berada dalam scope user.",
            )
        if schedule.schedule_status != "DRAFT":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hanya schedule DRAFT yang bisa dipublish.",
            )
        schedule.schedule_status = "PUBLISHED"
        schedule.updated_by = current_user.user.id
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def approve_work_schedule(
        self, current_user: CurrentUserContext, schedule_id: int
    ) -> WorkSchedule:
        schedule = self.repository.get_work_schedule(schedule_id)
        if schedule is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Work schedule tidak ditemukan.",
            )
        allowed_schedule_ids = {item.id for item in self.list_work_schedules(current_user)}
        if schedule.id not in allowed_schedule_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Work schedule tidak berada dalam scope user.",
            )
        if schedule.schedule_status != "PUBLISHED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hanya schedule PUBLISHED yang bisa diapprove.",
            )
        schedule.schedule_status = "APPROVED"
        schedule.approved_by = current_user.user.id
        schedule.updated_by = current_user.user.id
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def end_deployment(
        self,
        current_user: CurrentUserContext,
        deployment_id: int,
        payload: EndDeploymentRequest,
    ) -> EmployeeDeployment:
        deployment = self.repository.get_deployment(deployment_id)
        if deployment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment tidak ditemukan.",
            )
        allowed_deployment_ids = {item.id for item in self.list_deployments(current_user)}
        if deployment.id not in allowed_deployment_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Deployment tidak berada dalam scope user.",
            )
        deployment.end_date = payload.end_date
        deployment.deployment_status = "ENDED"
        if payload.notes:
            deployment.notes = payload.notes
        deployment.updated_by = current_user.user.id
        self.repository.create_deployment_history(
            DeploymentHistory(
                employee_deployment_id=deployment.id,
                action_type="END",
                old_client_site_id=deployment.client_site_id,
                new_client_site_id=deployment.client_site_id,
                old_site_post_id=deployment.site_post_id,
                new_site_post_id=deployment.site_post_id,
                action_date=payload.end_date,
                remarks=payload.notes,
                created_by=current_user.user.id,
                created_at=utc_now(),
            )
        )
        self.db.commit()
        self.db.refresh(deployment)
        return deployment
