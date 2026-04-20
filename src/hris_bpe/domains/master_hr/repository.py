from __future__ import annotations

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from hris_bpe.domains.master_hr.models import (
    Employee,
    EmployeeContract,
    EmployeeDocument,
    EmployeeEmergencyContact,
    EmployeeLifecycleEvent,
    GuardProfile,
)


class MasterHRRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_employees(self) -> list[Employee]:
        return list(self.db.execute(select(Employee).order_by(Employee.employee_number)).scalars())

    def list_guards(self) -> list[GuardProfile]:
        return list(self.db.execute(select(GuardProfile).order_by(GuardProfile.employee_id)).scalars())

    def get_employee_by_company_and_number(
        self, company_id: int, employee_number: str
    ) -> Employee | None:
        statement = select(Employee).where(
            Employee.company_id == company_id,
            func.lower(Employee.employee_number) == employee_number.lower(),
        )
        return self.db.execute(statement).scalar_one_or_none()

    def get_guard_profile_by_company_and_registration(
        self, company_id: int, guard_registration_number: str
    ) -> GuardProfile | None:
        statement = (
            select(GuardProfile)
            .join(Employee, Employee.id == GuardProfile.employee_id)
            .where(
                Employee.company_id == company_id,
                func.lower(GuardProfile.guard_registration_number)
                == guard_registration_number.lower(),
            )
        )
        return self.db.execute(statement).scalar_one_or_none()

    def create_employee(self, item: Employee) -> Employee:
        self.db.add(item)
        self.db.flush()
        return item

    def create_guard_profile(self, item: GuardProfile) -> GuardProfile:
        self.db.add(item)
        self.db.flush()
        return item

    def create_contract(self, item: EmployeeContract) -> EmployeeContract:
        self.db.add(item)
        self.db.flush()
        return item

    def list_employee_lifecycle_events(
        self, employee_id: int
    ) -> list[EmployeeLifecycleEvent]:
        statement = (
            select(EmployeeLifecycleEvent)
            .where(EmployeeLifecycleEvent.employee_id == employee_id)
            .order_by(
                desc(EmployeeLifecycleEvent.effective_date),
                desc(EmployeeLifecycleEvent.id),
            )
        )
        return list(self.db.execute(statement).scalars())

    def create_employee_lifecycle_event(
        self, item: EmployeeLifecycleEvent
    ) -> EmployeeLifecycleEvent:
        self.db.add(item)
        self.db.flush()
        return item

    def list_employee_emergency_contacts(
        self, employee_id: int
    ) -> list[EmployeeEmergencyContact]:
        statement = (
            select(EmployeeEmergencyContact)
            .where(EmployeeEmergencyContact.employee_id == employee_id)
            .order_by(
                desc(EmployeeEmergencyContact.is_primary),
                EmployeeEmergencyContact.contact_name,
            )
        )
        return list(self.db.execute(statement).scalars())

    def create_employee_emergency_contact(
        self, item: EmployeeEmergencyContact
    ) -> EmployeeEmergencyContact:
        self.db.add(item)
        self.db.flush()
        return item

    def list_employee_documents(self, employee_id: int) -> list[EmployeeDocument]:
        statement = (
            select(EmployeeDocument)
            .where(EmployeeDocument.employee_id == employee_id)
            .order_by(
                desc(EmployeeDocument.active_flag),
                EmployeeDocument.document_type,
                EmployeeDocument.document_name,
            )
        )
        return list(self.db.execute(statement).scalars())

    def create_employee_document(self, item: EmployeeDocument) -> EmployeeDocument:
        self.db.add(item)
        self.db.flush()
        return item

    def get_employee(self, employee_id: int) -> Employee | None:
        return self.db.get(Employee, employee_id)

    def get_employee_ids_with_deployments_in_sites(self, site_ids: set[int]) -> set[int]:
        if not site_ids:
            return set()
        from hris_bpe.domains.workforce_operations.models import EmployeeDeployment

        statement = select(EmployeeDeployment.employee_id).where(
            EmployeeDeployment.client_site_id.in_(site_ids)
        )
        return {row[0] for row in self.db.execute(statement).all()}
