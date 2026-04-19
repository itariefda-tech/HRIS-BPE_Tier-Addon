from fastapi import APIRouter, Depends

from hris_bpe.common.dependencies import DbSession, require_permissions
from hris_bpe.common.responses import success_payload
from hris_bpe.domains.master_hr.schemas import (
    EmployeeContractCreateRequest,
    EmployeeContractRead,
    EmployeeCreateRequest,
    EmployeeRead,
    GuardProfileCreateRequest,
    GuardProfileRead,
)
from hris_bpe.domains.master_hr.service import MasterHRService


router = APIRouter(prefix="/master-hr", tags=["master-hr"])


@router.get("/employees")
def list_employees(
    db: DbSession,
    current_user=Depends(require_permissions("employees.read")),
):
    service = MasterHRService(db)
    items = [
        EmployeeRead.model_validate(item).model_dump(mode="json")
        for item in service.list_employees(current_user)
    ]
    return success_payload("Daftar employee berhasil diambil.", data=items, meta={"total": len(items)})


@router.post("/employees")
def create_employee(
    payload: EmployeeCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("employees.manage")),
):
    service = MasterHRService(db)
    item = service.create_employee(current_user, payload)
    return success_payload("Employee berhasil dibuat.", data=EmployeeRead.model_validate(item).model_dump(mode="json"))


@router.get("/guards")
def list_guards(
    db: DbSession,
    current_user=Depends(require_permissions("employees.read")),
):
    service = MasterHRService(db)
    items = [
        GuardProfileRead.model_validate(item).model_dump(mode="json")
        for item in service.list_guards(current_user)
    ]
    return success_payload("Daftar guard profile berhasil diambil.", data=items, meta={"total": len(items)})


@router.post("/guards")
def create_guard_profile(
    payload: GuardProfileCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("guards.manage")),
):
    service = MasterHRService(db)
    item = service.create_guard_profile(current_user, payload)
    return success_payload("Guard profile berhasil dibuat.", data=GuardProfileRead.model_validate(item).model_dump(mode="json"))


@router.post("/employees/{employee_id}/contracts")
def create_employee_contract(
    employee_id: int,
    payload: EmployeeContractCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("employee_contracts.manage")),
):
    service = MasterHRService(db)
    item = service.create_contract(current_user, payload.model_copy(update={"employee_id": employee_id}))
    return success_payload("Employee contract berhasil dibuat.", data=EmployeeContractRead.model_validate(item).model_dump(mode="json"))
