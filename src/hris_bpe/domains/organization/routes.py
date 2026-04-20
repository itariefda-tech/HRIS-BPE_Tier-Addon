from fastapi import APIRouter, Depends

from hris_bpe.common.dependencies import DbSession, require_permissions
from hris_bpe.common.responses import success_payload
from hris_bpe.domains.organization.schemas import (
    BranchCreateRequest,
    BranchRead,
    CompanyCreateRequest,
    CompanyRead,
    CompanySettingsUpdateRequest,
    DepartmentCreateRequest,
    DepartmentRead,
    PositionCreateRequest,
    PositionRead,
)
from hris_bpe.domains.organization.service import OrganizationService


router = APIRouter(prefix="/organization", tags=["organization"])


@router.get("/companies")
def list_companies(
    db: DbSession,
    current_user=Depends(require_permissions("companies.read")),
):
    service = OrganizationService(db)
    items = [
        CompanyRead.model_validate(item).model_dump(mode="json")
        for item in service.list_companies(current_user)
    ]
    return success_payload("Daftar company berhasil diambil.", data=items, meta={"total": len(items)})


@router.post("/companies")
def create_company(
    payload: CompanyCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("companies.manage")),
):
    service = OrganizationService(db)
    item = service.create_company(current_user, payload)
    return success_payload("Company berhasil dibuat.", data=CompanyRead.model_validate(item).model_dump(mode="json"))


@router.put("/companies/{company_id}/settings")
def update_company_settings(
    company_id: int,
    payload: CompanySettingsUpdateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("companies.manage")),
):
    service = OrganizationService(db)
    item = service.update_company_settings(current_user, company_id, payload)
    return success_payload(
        "Setting company berhasil diperbarui.",
        data=CompanyRead.model_validate(item).model_dump(mode="json"),
    )


@router.get("/branches")
def list_branches(
    db: DbSession,
    current_user=Depends(require_permissions("branches.read")),
):
    service = OrganizationService(db)
    items = [
        BranchRead.model_validate(item).model_dump(mode="json")
        for item in service.list_branches(current_user)
    ]
    return success_payload("Daftar branch berhasil diambil.", data=items, meta={"total": len(items)})


@router.post("/branches")
def create_branch(
    payload: BranchCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("branches.manage")),
):
    service = OrganizationService(db)
    item = service.create_branch(current_user, payload)
    return success_payload("Branch berhasil dibuat.", data=BranchRead.model_validate(item).model_dump(mode="json"))


@router.get("/departments")
def list_departments(
    db: DbSession,
    current_user=Depends(require_permissions("departments.read")),
):
    service = OrganizationService(db)
    items = [
        DepartmentRead.model_validate(item).model_dump(mode="json")
        for item in service.list_departments(current_user)
    ]
    return success_payload("Daftar department berhasil diambil.", data=items, meta={"total": len(items)})


@router.post("/departments")
def create_department(
    payload: DepartmentCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("departments.manage")),
):
    service = OrganizationService(db)
    item = service.create_department(current_user, payload)
    return success_payload("Department berhasil dibuat.", data=DepartmentRead.model_validate(item).model_dump(mode="json"))


@router.get("/positions")
def list_positions(
    db: DbSession,
    current_user=Depends(require_permissions("positions.read")),
):
    service = OrganizationService(db)
    items = [
        PositionRead.model_validate(item).model_dump(mode="json")
        for item in service.list_positions(current_user)
    ]
    return success_payload("Daftar position berhasil diambil.", data=items, meta={"total": len(items)})


@router.post("/positions")
def create_position(
    payload: PositionCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("positions.manage")),
):
    service = OrganizationService(db)
    item = service.create_position(current_user, payload)
    return success_payload("Position berhasil dibuat.", data=PositionRead.model_validate(item).model_dump(mode="json"))
