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
    CompanySettingsUpdateRequest,
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

    @staticmethod
    def _raise_duplicate_code(detail: str) -> None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    def create_company(self, current_user: CurrentUserContext, payload: CompanyCreateRequest):
        if current_user.has_explicit_scope:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User dengan explicit scope tidak diizinkan membuat company baru.",
            )
        if self.repository.get_company_by_code(payload.code) is not None:
            self._raise_duplicate_code("Code company sudah digunakan.")
        item = Company(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_company(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_company_settings(
        self,
        current_user: CurrentUserContext,
        company_id: int,
        payload: CompanySettingsUpdateRequest,
    ):
        if payload.default_language is None and payload.default_theme is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimal satu setting company harus dikirim.",
            )
        item = self.repository.get_company(company_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company tidak ditemukan.",
            )
        ensure_company_access(
            current_user,
            item.id,
            detail="Company tidak berada dalam scope company user.",
        )
        if payload.default_language is not None:
            item.default_language = payload.default_language
        if payload.default_theme is not None:
            item.default_theme = payload.default_theme
        item.updated_by = current_user.user.id
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_branch(self, current_user: CurrentUserContext, payload: BranchCreateRequest):
        ensure_company_access(current_user, payload.company_id, detail="Branch tidak berada dalam scope company user.")
        if self.repository.get_branch_by_company_and_code(payload.company_id, payload.code) is not None:
            self._raise_duplicate_code("Code branch sudah digunakan pada company ini.")
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
        if (
            self.repository.get_department_by_company_and_code(payload.company_id, payload.code)
            is not None
        ):
            self._raise_duplicate_code("Code department sudah digunakan pada company ini.")
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
        if self.repository.get_position_by_company_and_code(payload.company_id, payload.code) is not None:
            self._raise_duplicate_code("Code position sudah digunakan pada company ini.")
        item = Position(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_position(item)
        self.db.commit()
        self.db.refresh(item)
        return item
