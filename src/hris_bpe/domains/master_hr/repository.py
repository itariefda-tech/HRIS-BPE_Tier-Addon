from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from hris_bpe.domains.master_hr.models import Employee, EmployeeContract, GuardProfile


class MasterHRRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_employees(self) -> list[Employee]:
        return list(self.db.execute(select(Employee).order_by(Employee.employee_number)).scalars())

    def list_guards(self) -> list[GuardProfile]:
        return list(self.db.execute(select(GuardProfile).order_by(GuardProfile.employee_id)).scalars())

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
