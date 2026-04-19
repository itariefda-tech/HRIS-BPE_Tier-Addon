import json

from fastapi import APIRouter, Depends, Query

from hris_bpe.common.dependencies import DbSession, require_permissions
from hris_bpe.common.responses import success_payload
from hris_bpe.domains.access_control.repository import AccessControlRepository
from hris_bpe.domains.access_control.schemas import (
    AccessControlAuditLogRead,
    AssignRolesRequest,
    PermissionRead,
    RoleRead,
    UserCreateRequest,
    UserRead,
    UserScopeAccessCreateRequest,
    UserScopeAccessRead,
)
from hris_bpe.domains.access_control.service import AccessControlService


router = APIRouter(prefix="/access-control", tags=["access-control"])


def _serialize_user(repository: AccessControlRepository, item) -> dict:
    payload = UserRead.model_validate(item).model_dump(mode="json")
    payload["role_codes"] = [role.code for role in repository.list_roles_for_user(item.id)]
    return payload


@router.get("/users")
def list_users(
    db: DbSession,
    current_user=Depends(require_permissions("users.read")),
):
    repository = AccessControlRepository(db)
    service = AccessControlService(db)
    items = [_serialize_user(repository, item) for item in service.list_users(current_user)]
    return success_payload("Daftar user berhasil diambil.", data=items, meta={"total": len(items)})


@router.post("/users")
def create_user(
    payload: UserCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("users.manage")),
):
    service = AccessControlService(db)
    repository = AccessControlRepository(db)
    user = service.create_user(current_user, payload)
    return success_payload("User berhasil dibuat.", data=_serialize_user(repository, user))


@router.post("/users/{user_id}/roles")
def assign_roles(
    user_id: int,
    payload: AssignRolesRequest,
    db: DbSession,
    current_user=Depends(require_permissions("users.assign_roles")),
):
    service = AccessControlService(db)
    repository = AccessControlRepository(db)
    user = service.assign_roles(current_user, user_id, payload)
    return success_payload("Role user berhasil diperbarui.", data=_serialize_user(repository, user))


@router.get("/users/{user_id}/scopes")
def list_user_scopes(
    user_id: int,
    db: DbSession,
    current_user=Depends(require_permissions("users.read")),
):
    service = AccessControlService(db)
    items = [
        UserScopeAccessRead.model_validate(item).model_dump(mode="json")
        for item in service.list_scopes(user_id)
    ]
    return success_payload("Scope user berhasil diambil.", data=items, meta={"total": len(items)})


@router.put("/users/{user_id}/scopes")
def replace_user_scopes(
    user_id: int,
    payload: list[UserScopeAccessCreateRequest],
    db: DbSession,
    current_user=Depends(require_permissions("users.assign_roles")),
):
    service = AccessControlService(db)
    items = [
        UserScopeAccessRead.model_validate(item).model_dump(mode="json")
        for item in service.replace_scopes(current_user, user_id, payload)
    ]
    return success_payload("Scope user berhasil diperbarui.", data=items, meta={"total": len(items)})


@router.get("/audit-logs")
def list_audit_logs(
    db: DbSession,
    target_user_id: int | None = Query(default=None),
    action_type: str | None = Query(default=None),
    current_user=Depends(require_permissions("users.read")),
):
    service = AccessControlService(db)
    items = [
        AccessControlAuditLogRead(
            id=item.id,
            actor_user_id=item.actor_user_id,
            target_user_id=item.target_user_id,
            action_type=item.action_type,
            entity_name=item.entity_name,
            old_data=json.loads(item.old_payload) if item.old_payload else None,
            new_data=json.loads(item.new_payload) if item.new_payload else None,
            remarks=item.remarks,
            created_at=item.created_at,
        ).model_dump(mode="json")
        for item in service.list_audit_logs(
            current_user,
            target_user_id=target_user_id,
            action_type=action_type,
        )
    ]
    return success_payload(
        "Audit log access control berhasil diambil.",
        data=items,
        meta={"total": len(items)},
    )


@router.get("/roles")
def list_roles(
    db: DbSession,
    current_user=Depends(require_permissions("roles.read")),
):
    service = AccessControlService(db)
    items = [
        RoleRead.model_validate(item).model_dump(mode="json")
        for item in service.list_roles(current_user)
    ]
    return success_payload("Daftar role berhasil diambil.", data=items, meta={"total": len(items)})


@router.get("/permissions")
def list_permissions(
    db: DbSession,
    current_user=Depends(require_permissions("permissions.read")),
):
    service = AccessControlService(db)
    items = [
        PermissionRead.model_validate(item).model_dump(mode="json")
        for item in service.list_permissions()
    ]
    return success_payload("Daftar permission berhasil diambil.", data=items, meta={"total": len(items)})
