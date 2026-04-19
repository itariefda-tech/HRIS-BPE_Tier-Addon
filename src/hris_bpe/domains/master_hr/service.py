from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hris_bpe.common.dependencies import CurrentUserContext
from hris_bpe.common.scope import ensure_company_access, filter_items_by_company_scope, has_unscoped_permission
from hris_bpe.domains.master_hr.models import Employee, EmployeeContract, GuardProfile
from hris_bpe.domains.master_hr.repository import MasterHRRepository
from hris_bpe.domains.master_hr.schemas import (
    EmployeeContractCreateRequest,
    EmployeeCreateRequest,
    GuardProfileCreateRequest,
)
from hris_bpe.domains.organization.models import Branch, Department, Position


class MasterHRService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = MasterHRRepository(db)

    def list_employees(self, current_user: CurrentUserContext):
        items = filter_items_by_company_scope(
            current_user,
            self.repository.list_employees(),
            lambda item: item.company_id,
        )
        if has_unscoped_permission(current_user, "employees.manage"):
            return items
        if current_user.branch_scope_ids:
            items = [item for item in items if item.branch_id in current_user.branch_scope_ids]
        if current_user.site_scope_ids:
            employee_ids = self.repository.get_employee_ids_with_deployments_in_sites(
                current_user.site_scope_ids
            )
            items = [item for item in items if item.id in employee_ids]
        if current_user.user.employee_id is not None and "employees.manage" not in current_user.permission_codes:
            items = [item for item in items if item.id == current_user.user.employee_id]
        return items

    def list_guards(self, current_user: CurrentUserContext):
        allowed_employee_ids = {item.id for item in self.list_employees(current_user)}
        return [
            item for item in self.repository.list_guards() if item.employee_id in allowed_employee_ids
        ]

    def create_employee(self, current_user: CurrentUserContext, payload: EmployeeCreateRequest):
        ensure_company_access(
            current_user,
            payload.company_id,
            detail="Employee tidak berada dalam scope company user.",
        )
        branch = self.db.get(Branch, payload.branch_id)
        if branch is None or branch.company_id != payload.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Branch employee tidak valid untuk company yang dipilih.",
            )
        if payload.department_id is not None:
            department = self.db.get(Department, payload.department_id)
            if department is None or department.company_id != payload.company_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department employee tidak valid untuk company yang dipilih.",
                )
        if payload.position_id is not None:
            position = self.db.get(Position, payload.position_id)
            if position is None or position.company_id != payload.company_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Position employee tidak valid untuk company yang dipilih.",
                )
        item = Employee(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_employee(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_guard_profile(
        self, current_user: CurrentUserContext, payload: GuardProfileCreateRequest
    ):
        employee = self.repository.get_employee(payload.employee_id)
        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee tidak ditemukan.",
            )
        ensure_company_access(
            current_user,
            employee.company_id,
            detail="Guard profile tidak berada dalam scope company user.",
        )
        item = GuardProfile(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_guard_profile(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_contract(
        self, current_user: CurrentUserContext, payload: EmployeeContractCreateRequest
    ):
        employee = self.repository.get_employee(payload.employee_id)
        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee tidak ditemukan.",
            )
        ensure_company_access(
            current_user,
            employee.company_id,
            detail="Employee contract tidak berada dalam scope company user.",
        )
        item = EmployeeContract(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_contract(item)
        self.db.commit()
        self.db.refresh(item)
        return item
