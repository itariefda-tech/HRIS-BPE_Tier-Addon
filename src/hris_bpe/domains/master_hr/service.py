from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hris_bpe.common.dependencies import CurrentUserContext
from hris_bpe.common.scope import (
    ensure_company_access,
    filter_items_by_company_scope,
    has_unscoped_permission,
)
from hris_bpe.domains.master_hr.models import (
    Employee,
    EmployeeContract,
    EmployeeDocument,
    EmployeeEmergencyContact,
    EmployeeLifecycleEvent,
    GuardProfile,
)
from hris_bpe.domains.master_hr.repository import MasterHRRepository
from hris_bpe.domains.master_hr.schemas import (
    EmployeeBatchImportRequest,
    EmployeeContractCreateRequest,
    EmployeeCreateRequest,
    EmployeeDocumentCreateRequest,
    EmployeeEmergencyContactCreateRequest,
    EmployeeLifecycleEventCreateRequest,
    EmployeeUpdateRequest,
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

    def _validate_employee_reference_scope(
        self,
        current_user: CurrentUserContext,
        *,
        company_id: int,
        branch_id: int,
        department_id: int | None,
        position_id: int | None,
    ) -> None:
        ensure_company_access(
            current_user,
            company_id,
            detail="Employee tidak berada dalam scope company user.",
        )
        if current_user.branch_scope_ids and branch_id not in current_user.branch_scope_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Branch employee tidak berada dalam scope branch user.",
            )
        branch = self.db.get(Branch, branch_id)
        if branch is None or branch.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Branch employee tidak valid untuk company yang dipilih.",
            )
        if department_id is not None:
            department = self.db.get(Department, department_id)
            if department is None or department.company_id != company_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department employee tidak valid untuk company yang dipilih.",
                )
        if position_id is not None:
            position = self.db.get(Position, position_id)
            if position is None or position.company_id != company_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Position employee tidak valid untuk company yang dipilih.",
                )

    def _get_accessible_employee(
        self, current_user: CurrentUserContext, employee_id: int
    ) -> Employee:
        employee = self.repository.get_employee(employee_id)
        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee tidak ditemukan.",
            )
        allowed_employee_ids = {item.id for item in self.list_employees(current_user)}
        if employee.id not in allowed_employee_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Employee tidak berada dalam scope akses user.",
            )
        return employee

    @staticmethod
    def _raise_duplicate_code(detail: str) -> None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    @staticmethod
    def _raise_invalid_lifecycle(detail: str) -> None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    def _create_employee_without_commit(
        self, current_user: CurrentUserContext, payload: EmployeeCreateRequest
    ) -> Employee:
        self._validate_employee_reference_scope(
            current_user,
            company_id=payload.company_id,
            branch_id=payload.branch_id,
            department_id=payload.department_id,
            position_id=payload.position_id,
        )
        if (
            self.repository.get_employee_by_company_and_number(
                payload.company_id,
                payload.employee_number,
            )
            is not None
        ):
            self._raise_duplicate_code("Employee number sudah digunakan pada company ini.")
        item = Employee(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_employee(item)
        return item

    def create_employee(self, current_user: CurrentUserContext, payload: EmployeeCreateRequest):
        item = self._create_employee_without_commit(current_user, payload)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_employee_detail(
        self, current_user: CurrentUserContext, employee_id: int
    ) -> Employee:
        return self._get_accessible_employee(current_user, employee_id)

    def update_employee(
        self,
        current_user: CurrentUserContext,
        employee_id: int,
        payload: EmployeeUpdateRequest,
    ) -> Employee:
        employee = self._get_accessible_employee(current_user, employee_id)
        changes = payload.model_dump(exclude_unset=True)
        if not changes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payload update employee kosong.",
            )

        new_branch_id = changes.get("branch_id", employee.branch_id)
        new_department_id = changes.get("department_id", employee.department_id)
        new_position_id = changes.get("position_id", employee.position_id)
        self._validate_employee_reference_scope(
            current_user,
            company_id=employee.company_id,
            branch_id=new_branch_id,
            department_id=new_department_id,
            position_id=new_position_id,
        )

        new_employee_number = changes.get("employee_number")
        if new_employee_number and new_employee_number != employee.employee_number:
            existing_employee = self.repository.get_employee_by_company_and_number(
                employee.company_id,
                new_employee_number,
            )
            if existing_employee is not None and existing_employee.id != employee.id:
                self._raise_duplicate_code(
                    "Employee number sudah digunakan pada company ini."
                )

        for field_name, value in changes.items():
            setattr(employee, field_name, value)
        employee.updated_by = current_user.user.id
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def import_employees_batch(
        self, current_user: CurrentUserContext, payload: EmployeeBatchImportRequest
    ) -> tuple[list[dict], dict]:
        results: list[dict] = []
        created_count = 0
        failed_count = 0
        stopped_early = False

        for row_no, employee_payload in enumerate(payload.employees, start=1):
            try:
                item = self._create_employee_without_commit(current_user, employee_payload)
                self.db.commit()
                self.db.refresh(item)
                results.append(
                    {
                        "row_no": row_no,
                        "status": "CREATED",
                        "employee_number": employee_payload.employee_number,
                        "company_id": employee_payload.company_id,
                        "full_name": employee_payload.full_name,
                        "message": "Employee berhasil diimport.",
                        "employee": item,
                    }
                )
                created_count += 1
            except HTTPException as exc:
                self.db.rollback()
                results.append(
                    {
                        "row_no": row_no,
                        "status": "FAILED",
                        "employee_number": employee_payload.employee_number,
                        "company_id": employee_payload.company_id,
                        "full_name": employee_payload.full_name,
                        "message": str(exc.detail),
                        "employee": None,
                    }
                )
                failed_count += 1
                if payload.stop_on_error:
                    stopped_early = True
                    break
            except Exception:
                self.db.rollback()
                results.append(
                    {
                        "row_no": row_no,
                        "status": "FAILED",
                        "employee_number": employee_payload.employee_number,
                        "company_id": employee_payload.company_id,
                        "full_name": employee_payload.full_name,
                        "message": "Terjadi error internal saat import employee.",
                        "employee": None,
                    }
                )
                failed_count += 1
                if payload.stop_on_error:
                    stopped_early = True
                    break

        return (
            results,
            {
                "total": len(results),
                "requested_total": len(payload.employees),
                "created": created_count,
                "failed": failed_count,
                "stopped_early": stopped_early,
            },
        )

    def create_guard_profile(
        self, current_user: CurrentUserContext, payload: GuardProfileCreateRequest
    ):
        employee = self._get_accessible_employee(current_user, payload.employee_id)
        if payload.guard_registration_number and (
            self.repository.get_guard_profile_by_company_and_registration(
                employee.company_id,
                payload.guard_registration_number,
            )
            is not None
        ):
            self._raise_duplicate_code(
                "Guard registration number sudah digunakan pada company ini."
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
        self._get_accessible_employee(current_user, payload.employee_id)
        item = EmployeeContract(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_contract(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_employee_lifecycle_events(
        self, current_user: CurrentUserContext, employee_id: int
    ):
        self._get_accessible_employee(current_user, employee_id)
        return self.repository.list_employee_lifecycle_events(employee_id)

    def create_employee_lifecycle_event(
        self,
        current_user: CurrentUserContext,
        employee_id: int,
        payload: EmployeeLifecycleEventCreateRequest,
    ) -> tuple[EmployeeLifecycleEvent, Employee]:
        employee = self._get_accessible_employee(current_user, employee_id)

        action_type = payload.action_type
        new_employee_status = employee.employee_status
        new_employment_status = employee.employment_status
        new_branch_id = employee.branch_id
        new_department_id = employee.department_id
        new_position_id = employee.position_id
        new_hire_date = employee.hire_date
        new_resign_date = employee.resign_date

        if action_type == "ONBOARD":
            new_employee_status = payload.new_employee_status or "ACTIVE"
            if payload.new_employment_status is not None:
                new_employment_status = payload.new_employment_status
            if employee.hire_date is None:
                new_hire_date = payload.effective_date
            new_resign_date = None
        elif action_type == "TRANSFER":
            if (
                payload.new_branch_id is None
                and payload.new_department_id is None
                and payload.new_position_id is None
            ):
                self._raise_invalid_lifecycle(
                    "TRANSFER membutuhkan perubahan branch, department, atau position."
                )
            new_branch_id = payload.new_branch_id or employee.branch_id
            new_department_id = (
                payload.new_department_id
                if payload.new_department_id is not None
                else employee.department_id
            )
            new_position_id = (
                payload.new_position_id
                if payload.new_position_id is not None
                else employee.position_id
            )
        elif action_type == "STATUS_CHANGE":
            if (
                payload.new_employee_status is None
                and payload.new_employment_status is None
            ):
                self._raise_invalid_lifecycle(
                    "STATUS_CHANGE membutuhkan new_employee_status atau new_employment_status."
                )
            if payload.new_employee_status is not None:
                new_employee_status = payload.new_employee_status
            if payload.new_employment_status is not None:
                new_employment_status = payload.new_employment_status
        elif action_type == "SUSPEND":
            new_employee_status = "SUSPENDED"
        elif action_type == "RESIGN":
            new_employee_status = "RESIGNED"
            new_resign_date = payload.effective_date
        elif action_type == "TERMINATE":
            new_employee_status = "TERMINATED"
            new_resign_date = payload.effective_date
        elif action_type == "REACTIVATE":
            new_employee_status = payload.new_employee_status or "ACTIVE"
            if payload.new_employment_status is not None:
                new_employment_status = payload.new_employment_status
            new_resign_date = None
            if employee.hire_date is None:
                new_hire_date = payload.effective_date
        else:
            self._raise_invalid_lifecycle(
                f"Action type lifecycle tidak valid: {payload.action_type}"
            )

        self._validate_employee_reference_scope(
            current_user,
            company_id=employee.company_id,
            branch_id=new_branch_id,
            department_id=new_department_id,
            position_id=new_position_id,
        )

        has_change = any(
            [
                employee.employee_status != new_employee_status,
                employee.employment_status != new_employment_status,
                employee.branch_id != new_branch_id,
                employee.department_id != new_department_id,
                employee.position_id != new_position_id,
                employee.hire_date != new_hire_date,
                employee.resign_date != new_resign_date,
            ]
        )
        if not has_change:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Lifecycle employee tidak mengubah data employee.",
            )

        event = EmployeeLifecycleEvent(
            employee_id=employee.id,
            action_type=action_type,
            effective_date=payload.effective_date,
            old_employee_status=employee.employee_status,
            new_employee_status=new_employee_status,
            old_employment_status=employee.employment_status,
            new_employment_status=new_employment_status,
            old_branch_id=employee.branch_id,
            new_branch_id=new_branch_id,
            old_department_id=employee.department_id,
            new_department_id=new_department_id,
            old_position_id=employee.position_id,
            new_position_id=new_position_id,
            old_hire_date=employee.hire_date,
            new_hire_date=new_hire_date,
            old_resign_date=employee.resign_date,
            new_resign_date=new_resign_date,
            remarks=payload.remarks,
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )

        employee.employee_status = new_employee_status
        employee.employment_status = new_employment_status
        employee.branch_id = new_branch_id
        employee.department_id = new_department_id
        employee.position_id = new_position_id
        employee.hire_date = new_hire_date
        employee.resign_date = new_resign_date
        employee.updated_by = current_user.user.id

        self.repository.create_employee_lifecycle_event(event)
        self.db.commit()
        self.db.refresh(event)
        self.db.refresh(employee)
        return event, employee

    def list_employee_emergency_contacts(
        self, current_user: CurrentUserContext, employee_id: int
    ):
        self._get_accessible_employee(current_user, employee_id)
        return self.repository.list_employee_emergency_contacts(employee_id)

    def create_employee_emergency_contact(
        self,
        current_user: CurrentUserContext,
        employee_id: int,
        payload: EmployeeEmergencyContactCreateRequest,
    ):
        self._get_accessible_employee(current_user, employee_id)
        item = EmployeeEmergencyContact(
            employee_id=employee_id,
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_employee_emergency_contact(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_employee_documents(self, current_user: CurrentUserContext, employee_id: int):
        self._get_accessible_employee(current_user, employee_id)
        return self.repository.list_employee_documents(employee_id)

    def create_employee_document(
        self,
        current_user: CurrentUserContext,
        employee_id: int,
        payload: EmployeeDocumentCreateRequest,
    ):
        self._get_accessible_employee(current_user, employee_id)
        item = EmployeeDocument(
            employee_id=employee_id,
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_employee_document(item)
        self.db.commit()
        self.db.refresh(item)
        return item
