from fastapi import APIRouter, Depends

from hris_bpe.common.dependencies import DbSession, require_permissions
from hris_bpe.common.responses import success_payload
from hris_bpe.domains.master_hr.schemas import (
    EmployeeBatchImportItemRead,
    EmployeeBatchImportRequest,
    EmployeeContractCreateRequest,
    EmployeeContractRead,
    EmployeeCreateRequest,
    EmployeeDocumentCreateRequest,
    EmployeeDocumentRead,
    EmployeeEmergencyContactCreateRequest,
    EmployeeEmergencyContactRead,
    EmployeeLifecycleEventCreateRequest,
    EmployeeLifecycleEventRead,
    EmployeeLifecycleTransitionRead,
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


@router.post("/employees/imports/batch")
def import_batch_employees(
    payload: EmployeeBatchImportRequest,
    db: DbSession,
    current_user=Depends(require_permissions("employees.manage")),
):
    service = MasterHRService(db)
    results, meta = service.import_employees_batch(current_user, payload)
    items = [
        EmployeeBatchImportItemRead(
            **{
                **item,
                "employee": (
                    EmployeeRead.model_validate(item["employee"])
                    if item["employee"] is not None
                    else None
                ),
            }
        ).model_dump(mode="json")
        for item in results
    ]
    return success_payload(
        "Import batch employee selesai.",
        data=items,
        meta=meta,
    )


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


@router.get("/employees/{employee_id}/lifecycle-events")
def list_employee_lifecycle_events(
    employee_id: int,
    db: DbSession,
    current_user=Depends(require_permissions("employees.read")),
):
    service = MasterHRService(db)
    items = [
        EmployeeLifecycleEventRead.model_validate(item).model_dump(mode="json")
        for item in service.list_employee_lifecycle_events(current_user, employee_id)
    ]
    return success_payload(
        "Riwayat lifecycle employee berhasil diambil.",
        data=items,
        meta={"total": len(items)},
    )


@router.post("/employees/{employee_id}/lifecycle-events")
def create_employee_lifecycle_event(
    employee_id: int,
    payload: EmployeeLifecycleEventCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("employees.manage")),
):
    service = MasterHRService(db)
    event, employee = service.create_employee_lifecycle_event(
        current_user,
        employee_id,
        payload,
    )
    return success_payload(
        "Lifecycle employee berhasil diperbarui.",
        data=EmployeeLifecycleTransitionRead(
            event=EmployeeLifecycleEventRead.model_validate(event),
            employee=EmployeeRead.model_validate(employee),
        ).model_dump(mode="json"),
    )


@router.get("/employees/{employee_id}/emergency-contacts")
def list_employee_emergency_contacts(
    employee_id: int,
    db: DbSession,
    current_user=Depends(require_permissions("employees.read")),
):
    service = MasterHRService(db)
    items = [
        EmployeeEmergencyContactRead.model_validate(item).model_dump(mode="json")
        for item in service.list_employee_emergency_contacts(current_user, employee_id)
    ]
    return success_payload(
        "Daftar emergency contact employee berhasil diambil.",
        data=items,
        meta={"total": len(items)},
    )


@router.post("/employees/{employee_id}/emergency-contacts")
def create_employee_emergency_contact(
    employee_id: int,
    payload: EmployeeEmergencyContactCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("employees.manage")),
):
    service = MasterHRService(db)
    item = service.create_employee_emergency_contact(current_user, employee_id, payload)
    return success_payload(
        "Emergency contact employee berhasil dibuat.",
        data=EmployeeEmergencyContactRead.model_validate(item).model_dump(mode="json"),
    )


@router.get("/employees/{employee_id}/documents")
def list_employee_documents(
    employee_id: int,
    db: DbSession,
    current_user=Depends(require_permissions("employees.read")),
):
    service = MasterHRService(db)
    items = [
        EmployeeDocumentRead.model_validate(item).model_dump(mode="json")
        for item in service.list_employee_documents(current_user, employee_id)
    ]
    return success_payload(
        "Daftar dokumen employee berhasil diambil.",
        data=items,
        meta={"total": len(items)},
    )


@router.post("/employees/{employee_id}/documents")
def create_employee_document(
    employee_id: int,
    payload: EmployeeDocumentCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("employees.manage")),
):
    service = MasterHRService(db)
    item = service.create_employee_document(current_user, employee_id, payload)
    return success_payload(
        "Dokumen employee berhasil dibuat.",
        data=EmployeeDocumentRead.model_validate(item).model_dump(mode="json"),
    )
