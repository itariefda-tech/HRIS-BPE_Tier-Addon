from fastapi import APIRouter, Depends

from hris_bpe.common.dependencies import CurrentUser, DbSession, require_permissions
from hris_bpe.common.responses import success_payload
from hris_bpe.domains.workforce_operations.schemas import (
    BulkScheduleGenerateRequest,
    DeploymentHistoryRead,
    EndDeploymentRequest,
    EmployeeDeploymentCreateRequest,
    EmployeeDeploymentRead,
    EmployeeDeploymentUpdateRequest,
    MyWorkScheduleRead,
    ShiftTypeCreateRequest,
    ShiftTypeRead,
    WorkScheduleCreateRequest,
    WorkScheduleRead,
    WorkScheduleUpdateRequest,
)
from hris_bpe.domains.workforce_operations.service import WorkforceOperationsService


router = APIRouter(prefix="/workforce-operations", tags=["workforce-operations"])
my_router = APIRouter(prefix="/my", tags=["my"])


@router.get("/deployments")
def list_deployments(
    db: DbSession,
    current_user=Depends(require_permissions("deployments.read")),
):
    service = WorkforceOperationsService(db)
    items = [
        EmployeeDeploymentRead.model_validate(item).model_dump(mode="json")
        for item in service.list_deployments(current_user)
    ]
    return success_payload("Daftar deployment berhasil diambil.", data=items, meta={"total": len(items)})


@router.post("/deployments")
def create_deployment(
    payload: EmployeeDeploymentCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("deployments.manage")),
):
    service = WorkforceOperationsService(db)
    item = service.create_deployment(current_user, payload, current_user.user.id)
    return success_payload("Deployment berhasil dibuat.", data=EmployeeDeploymentRead.model_validate(item).model_dump(mode="json"))


@router.get("/deployments/{deployment_id}")
def get_deployment_detail(
    deployment_id: int,
    db: DbSession,
    current_user=Depends(require_permissions("deployments.read")),
):
    service = WorkforceOperationsService(db)
    item = service.get_deployment_detail(current_user, deployment_id)
    return success_payload(
        "Detail deployment berhasil diambil.",
        data=EmployeeDeploymentRead.model_validate(item).model_dump(mode="json"),
    )


@router.put("/deployments/{deployment_id}")
def update_deployment(
    deployment_id: int,
    payload: EmployeeDeploymentUpdateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("deployments.manage")),
):
    service = WorkforceOperationsService(db)
    item = service.update_deployment(current_user, deployment_id, payload)
    return success_payload(
        "Deployment berhasil diperbarui.",
        data=EmployeeDeploymentRead.model_validate(item).model_dump(mode="json"),
    )


@router.get("/deployment-histories")
def list_deployment_histories(
    db: DbSession,
    current_user=Depends(require_permissions("deployments.read")),
):
    service = WorkforceOperationsService(db)
    items = [
        DeploymentHistoryRead.model_validate(item).model_dump(mode="json")
        for item in service.list_deployment_histories(current_user)
    ]
    return success_payload("Riwayat deployment berhasil diambil.", data=items, meta={"total": len(items)})


@router.post("/deployments/{deployment_id}/end")
def end_deployment(
    deployment_id: int,
    payload: EndDeploymentRequest,
    db: DbSession,
    current_user=Depends(require_permissions("deployments.manage")),
):
    service = WorkforceOperationsService(db)
    item = service.end_deployment(current_user, deployment_id, payload)
    return success_payload("Deployment berhasil diakhiri.", data=EmployeeDeploymentRead.model_validate(item).model_dump(mode="json"))


@router.get("/shift-types")
def list_shift_types(
    db: DbSession,
    current_user=Depends(require_permissions("shift_types.read")),
):
    service = WorkforceOperationsService(db)
    items = [
        ShiftTypeRead.model_validate(item).model_dump(mode="json")
        for item in service.list_shift_types(current_user)
    ]
    return success_payload("Daftar shift type berhasil diambil.", data=items, meta={"total": len(items)})


@router.post("/shift-types")
def create_shift_type(
    payload: ShiftTypeCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("shift_types.manage")),
):
    service = WorkforceOperationsService(db)
    item = service.create_shift_type(current_user, payload)
    return success_payload("Shift type berhasil dibuat.", data=ShiftTypeRead.model_validate(item).model_dump(mode="json"))


@router.get("/work-schedules")
def list_work_schedules(
    db: DbSession,
    current_user=Depends(require_permissions("schedules.read")),
):
    service = WorkforceOperationsService(db)
    items = [
        WorkScheduleRead.model_validate(item).model_dump(mode="json")
        for item in service.list_work_schedules(current_user)
    ]
    return success_payload("Daftar work schedule berhasil diambil.", data=items, meta={"total": len(items)})


@router.get("/work-schedules/{schedule_id}")
def get_work_schedule_detail(
    schedule_id: int,
    db: DbSession,
    current_user=Depends(require_permissions("schedules.read")),
):
    service = WorkforceOperationsService(db)
    item = service.get_work_schedule_detail(current_user, schedule_id)
    return success_payload(
        "Detail work schedule berhasil diambil.",
        data=WorkScheduleRead.model_validate(item).model_dump(mode="json"),
    )


@router.put("/work-schedules/{schedule_id}")
def update_work_schedule(
    schedule_id: int,
    payload: WorkScheduleUpdateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("schedules.manage")),
):
    service = WorkforceOperationsService(db)
    item = service.update_work_schedule(current_user, schedule_id, payload)
    return success_payload(
        "Work schedule berhasil diperbarui.",
        data=WorkScheduleRead.model_validate(item).model_dump(mode="json"),
    )


@router.post("/work-schedules")
def create_work_schedules(
    payload: WorkScheduleCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("schedules.manage")),
):
    service = WorkforceOperationsService(db)
    item = service.create_work_schedule(
        current_user=current_user,
        payload=payload,
        generated_by=current_user.user.id,
        approved_by=None,
    )
    return success_payload("Work schedule berhasil dibuat.", data=WorkScheduleRead.model_validate(item).model_dump(mode="json"))


@router.post("/work-schedules/generate")
def generate_bulk_work_schedules(
    payload: BulkScheduleGenerateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("schedules.manage")),
):
    service = WorkforceOperationsService(db)
    items = [
        WorkScheduleRead.model_validate(item).model_dump(mode="json")
        for item in service.generate_bulk_schedules(current_user, payload)
    ]
    return success_payload("Bulk work schedule berhasil dibuat.", data=items, meta={"total": len(items)})


@router.post("/work-schedules/{schedule_id}/publish")
def publish_work_schedule(
    schedule_id: int,
    db: DbSession,
    current_user=Depends(require_permissions("schedules.manage")),
):
    service = WorkforceOperationsService(db)
    item = service.publish_work_schedule(current_user, schedule_id)
    return success_payload(
        "Work schedule berhasil dipublish.",
        data=WorkScheduleRead.model_validate(item).model_dump(mode="json"),
    )


@router.post("/work-schedules/{schedule_id}/approve")
def approve_work_schedule(
    schedule_id: int,
    db: DbSession,
    current_user=Depends(require_permissions("schedules.manage")),
):
    service = WorkforceOperationsService(db)
    item = service.approve_work_schedule(current_user, schedule_id)
    return success_payload(
        "Work schedule berhasil diapprove.",
        data=WorkScheduleRead.model_validate(item).model_dump(mode="json"),
    )


@my_router.get("/schedules")
def list_my_schedules(
    db: DbSession,
    current_user=Depends(require_permissions("schedules.read")),
):
    service = WorkforceOperationsService(db)
    items = [
        service.build_my_schedule_read(item).model_dump(mode="json")
        for item in service.list_my_schedules(current_user)
    ]
    return success_payload(
        "Daftar schedule saya berhasil diambil.",
        data=items,
        meta={"total": len(items)},
    )
