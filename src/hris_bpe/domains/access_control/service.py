from __future__ import annotations

import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hris_bpe.common.dependencies import CurrentUserContext
from hris_bpe.common.scope import ensure_company_access, resolve_company_scope_ids
from hris_bpe.common.security import hash_password
from hris_bpe.domains.access_control.models import AccessControlAuditLog, User
from hris_bpe.domains.access_control.repository import (
    AccessControlRepository,
    UserScopeAccessCreatePayload,
)
from hris_bpe.domains.access_control.schemas import (
    AssignRolesRequest,
    UserCreateRequest,
    UserScopeAccessCreateRequest,
)
from hris_bpe.domains.client_contract.models import Client
from hris_bpe.domains.master_hr.models import Employee
from hris_bpe.domains.organization.models import Branch
from hris_bpe.domains.site_operations.models import ClientSite


class AccessControlService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AccessControlRepository(db)

    def list_users(self, current_user: CurrentUserContext):
        allowed_company_ids = resolve_company_scope_ids(current_user)
        employee_company_map = {
            employee.id: employee.company_id for employee in self.db.query(Employee).all()
        }
        items: list[User] = []
        for user in self.repository.list_users():
            user_role_company_ids = {
                role.company_id
                for role in self.repository.list_roles_for_user(user.id)
                if role.company_id is not None
            }
            employee_company_id = (
                employee_company_map.get(user.employee_id)
                if user.employee_id is not None
                else None
            )
            if not allowed_company_ids:
                items.append(user)
                continue
            if user_role_company_ids.intersection(allowed_company_ids):
                items.append(user)
                continue
            if employee_company_id in allowed_company_ids:
                items.append(user)
        return items

    def list_roles(self, current_user: CurrentUserContext):
        return self.repository.list_roles(resolve_company_scope_ids(current_user))

    def list_permissions(self):
        return self.repository.list_permissions()

    @staticmethod
    def _serialize_role_codes(role_codes: list[str]) -> str:
        return json.dumps(sorted(role_codes))

    @staticmethod
    def _serialize_scope_items(items) -> str:
        normalized = sorted(
            [
                {
                    "scope_type": item.scope_type,
                    "company_id": item.company_id,
                    "branch_id": item.branch_id,
                    "client_site_id": item.client_site_id,
                }
                for item in items
            ],
            key=lambda item: (
                item["scope_type"],
                item["company_id"] or 0,
                item["branch_id"] or 0,
                item["client_site_id"] or 0,
            ),
        )
        return json.dumps(normalized, sort_keys=True)

    def _create_audit_log(
        self,
        *,
        actor_user_id: int,
        target_user_id: int,
        action_type: str,
        entity_name: str,
        old_payload: str | None,
        new_payload: str | None,
        remarks: str | None = None,
    ) -> None:
        if old_payload == new_payload:
            return
        self.repository.create_audit_log(
            AccessControlAuditLog(
                actor_user_id=actor_user_id,
                target_user_id=target_user_id,
                action_type=action_type,
                entity_name=entity_name,
                old_payload=old_payload,
                new_payload=new_payload,
                remarks=remarks,
            )
        )

    def create_user(self, current_user: CurrentUserContext, payload: UserCreateRequest) -> User:
        existing = self.repository.get_user_by_login(payload.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email user sudah terdaftar.",
            )
        roles = self.repository.get_roles_by_ids(payload.role_ids)
        if len(roles) != len(payload.role_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sebagian role tidak ditemukan.",
            )
        allowed_company_ids = resolve_company_scope_ids(current_user)
        if allowed_company_ids and any(
            role.company_id not in allowed_company_ids for role in roles
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ada role yang berada di luar scope company user.",
            )
        if payload.employee_id is not None:
            employee = self.db.get(Employee, payload.employee_id)
            if employee is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Employee tidak ditemukan.",
                )
            ensure_company_access(
                current_user,
                employee.company_id,
                detail="Employee user tidak berada dalam scope company user.",
            )
        user = User(
            employee_id=payload.employee_id,
            username=payload.username,
            email=payload.email.lower(),
            phone=payload.phone,
            password_hash=hash_password(payload.password),
            is_active=payload.is_active,
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_user(user)
        self.repository.assign_roles(user.id, [role.id for role in roles])
        self.db.commit()
        self.db.refresh(user)
        return user

    def assign_roles(
        self, current_user: CurrentUserContext, user_id: int, payload: AssignRolesRequest
    ) -> User:
        user = self.repository.get_user(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User tidak ditemukan.",
            )
        roles = self.repository.get_roles_by_ids(payload.role_ids)
        if len(roles) != len(payload.role_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sebagian role tidak ditemukan.",
            )
        allowed_company_ids = resolve_company_scope_ids(current_user)
        if allowed_company_ids and any(
            role.company_id not in allowed_company_ids for role in roles
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ada role yang berada di luar scope company user.",
            )
        old_role_payload = self._serialize_role_codes(
            [role.code for role in self.repository.list_roles_for_user(user.id)]
        )
        user.updated_by = current_user.user.id
        self.repository.assign_roles(user.id, [role.id for role in roles])
        new_role_payload = self._serialize_role_codes(
            [role.code for role in self.repository.list_roles_for_user(user.id)]
        )
        self._create_audit_log(
            actor_user_id=current_user.user.id,
            target_user_id=user.id,
            action_type="USER_ROLES_REPLACED",
            entity_name="roles",
            old_payload=old_role_payload,
            new_payload=new_role_payload,
            remarks="Perubahan assignment role user.",
        )
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_scopes(self, user_id: int):
        user = self.repository.get_user(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User tidak ditemukan.",
            )
        return self.repository.list_scopes_for_user(user_id)

    def list_audit_logs(
        self,
        current_user: CurrentUserContext,
        *,
        target_user_id: int | None = None,
        action_type: str | None = None,
    ):
        allowed_user_ids = {item.id for item in self.list_users(current_user)}
        normalized_action = action_type.strip().upper() if action_type else None
        return [
            item
            for item in self.repository.list_audit_logs(
                target_user_id=target_user_id,
                action_type=normalized_action,
            )
            if item.target_user_id in allowed_user_ids
        ]

    def replace_scopes(
        self,
        current_user: CurrentUserContext,
        user_id: int,
        payloads: list[UserScopeAccessCreateRequest],
    ):
        user = self.repository.get_user(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User tidak ditemukan.",
            )
        old_scope_payload = self._serialize_scope_items(
            self.repository.list_scopes_for_user(user.id)
        )
        normalized: list[UserScopeAccessCreatePayload] = []
        for payload in payloads:
            scope_type = payload.scope_type.strip().upper()
            if scope_type not in {"COMPANY", "BRANCH", "SITE"}:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Scope type tidak valid: {payload.scope_type}",
                )
            if scope_type == "COMPANY" and payload.company_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="company_id wajib untuk scope COMPANY.",
                )
            if scope_type == "BRANCH" and payload.branch_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="branch_id wajib untuk scope BRANCH.",
                )
            if scope_type == "SITE" and payload.client_site_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="client_site_id wajib untuk scope SITE.",
                )
            if payload.company_id is not None:
                ensure_company_access(
                    current_user,
                    payload.company_id,
                    detail="Scope company di luar company yang boleh dikelola user.",
                )
            if payload.branch_id is not None:
                branch = self.db.get(Branch, payload.branch_id)
                if branch is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Branch scope tidak ditemukan.",
                    )
                ensure_company_access(
                    current_user,
                    branch.company_id,
                    detail="Branch scope di luar company yang boleh dikelola user.",
                )
            if payload.client_site_id is not None:
                site = self.db.get(ClientSite, payload.client_site_id)
                if site is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Site scope tidak ditemukan.",
                    )
                client = self.db.get(Client, site.client_id)
                if client is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Client site scope tidak valid.",
                    )
                ensure_company_access(
                    current_user,
                    client.company_id,
                    detail="Site scope di luar company yang boleh dikelola user.",
                )
            normalized.append(
                UserScopeAccessCreatePayload(
                    scope_type=scope_type,
                    company_id=payload.company_id,
                    branch_id=payload.branch_id,
                    client_site_id=payload.client_site_id,
                )
            )
        user.updated_by = current_user.user.id
        items = self.repository.replace_scopes(
            user_id,
            normalized,
            actor_user_id=current_user.user.id,
        )
        new_scope_payload = self._serialize_scope_items(items)
        self._create_audit_log(
            actor_user_id=current_user.user.id,
            target_user_id=user.id,
            action_type="USER_SCOPES_REPLACED",
            entity_name="scopes",
            old_payload=old_scope_payload,
            new_payload=new_scope_payload,
            remarks="Perubahan scope akses user.",
        )
        self.db.commit()
        return items
