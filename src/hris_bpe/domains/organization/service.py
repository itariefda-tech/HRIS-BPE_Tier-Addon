from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hris_bpe.common.dependencies import CurrentUserContext
from hris_bpe.common.scope import ensure_company_access, filter_items_by_company_scope
from hris_bpe.domains.organization.models import Branch, Company, Department, Position
from hris_bpe.domains.organization.repository import OrganizationRepository
from hris_bpe.domains.organization.schemas import (
    BranchCreateRequest,
    CompanyCreateRequest,
    DepartmentCreateRequest,
    PositionCreateRequest,
)


class OrganizationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = OrganizationRepository(db)

    def list_companies(self, current_user: CurrentUserContext):
        return filter_items_by_company_scope(current_user, self.repository.list_companies(), lambda item: item.id)

    def list_branches(self, current_user: CurrentUserContext):
        return filter_items_by_company_scope(
            current_user,
            self.repository.list_branches(),
            lambda item: item.company_id,
        )

    def list_departments(self, current_user: CurrentUserContext):
        return filter_items_by_company_scope(
            current_user,
            self.repository.list_departments(),
            lambda item: item.company_id,
        )

    def list_positions(self, current_user: CurrentUserContext):
        return filter_items_by_company_scope(
            current_user,
            self.repository.list_positions(),
            lambda item: item.company_id,
        )

    def create_company(self, current_user: CurrentUserContext, payload: CompanyCreateRequest):
        if current_user.has_explicit_scope:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User dengan explicit scope tidak diizinkan membuat company baru.",
            )
        item = Company(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_company(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_branch(self, current_user: CurrentUserContext, payload: BranchCreateRequest):
        ensure_company_access(current_user, payload.company_id, detail="Branch tidak berada dalam scope company user.")
        item = Branch(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_branch(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_department(self, current_user: CurrentUserContext, payload: DepartmentCreateRequest):
        ensure_company_access(
            current_user,
            payload.company_id,
            detail="Department tidak berada dalam scope company user.",
        )
        item = Department(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_department(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_position(self, current_user: CurrentUserContext, payload: PositionCreateRequest):
        ensure_company_access(
            current_user,
            payload.company_id,
            detail="Position tidak berada dalam scope company user.",
        )
        item = Position(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_position(item)
        self.db.commit()
        self.db.refresh(item)
        return item
