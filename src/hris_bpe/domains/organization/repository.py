from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from hris_bpe.domains.organization.models import Branch, Company, Department, Position


class OrganizationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_companies(self) -> list[Company]:
        return list(self.db.execute(select(Company).order_by(Company.code)).scalars())

    def list_branches(self) -> list[Branch]:
        return list(self.db.execute(select(Branch).order_by(Branch.code)).scalars())

    def list_departments(self) -> list[Department]:
        return list(self.db.execute(select(Department).order_by(Department.code)).scalars())

    def list_positions(self) -> list[Position]:
        return list(self.db.execute(select(Position).order_by(Position.code)).scalars())

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

