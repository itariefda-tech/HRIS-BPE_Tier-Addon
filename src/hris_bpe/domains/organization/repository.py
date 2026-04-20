from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from hris_bpe.domains.organization.models import Branch, Company, Department, Position


class OrganizationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_companies(self) -> list[Company]:
        return list(self.db.execute(select(Company).order_by(Company.code)).scalars())

    def get_company(self, company_id: int) -> Company | None:
        return self.db.get(Company, company_id)

    def list_branches(self) -> list[Branch]:
        return list(self.db.execute(select(Branch).order_by(Branch.code)).scalars())

    def list_departments(self) -> list[Department]:
        return list(self.db.execute(select(Department).order_by(Department.code)).scalars())

    def list_positions(self) -> list[Position]:
        return list(self.db.execute(select(Position).order_by(Position.code)).scalars())

    def get_company_by_code(self, code: str) -> Company | None:
        statement = select(Company).where(func.lower(Company.code) == code.lower())
        return self.db.execute(statement).scalar_one_or_none()

    def get_branch_by_company_and_code(self, company_id: int, code: str) -> Branch | None:
        statement = select(Branch).where(
            Branch.company_id == company_id,
            func.lower(Branch.code) == code.lower(),
        )
        return self.db.execute(statement).scalar_one_or_none()

    def get_department_by_company_and_code(
        self, company_id: int, code: str
    ) -> Department | None:
        statement = select(Department).where(
            Department.company_id == company_id,
            func.lower(Department.code) == code.lower(),
        )
        return self.db.execute(statement).scalar_one_or_none()

    def get_position_by_company_and_code(self, company_id: int, code: str) -> Position | None:
        statement = select(Position).where(
            Position.company_id == company_id,
            func.lower(Position.code) == code.lower(),
        )
        return self.db.execute(statement).scalar_one_or_none()

    def create_company(self, item: Company) -> Company:
        self.db.add(item)
        self.db.flush()
        return item

    def create_branch(self, item: Branch) -> Branch:
        self.db.add(item)
        self.db.flush()
        return item

    def create_department(self, item: Department) -> Department:
        self.db.add(item)
        self.db.flush()
        return item

    def create_position(self, item: Position) -> Position:
        self.db.add(item)
        self.db.flush()
        return item
