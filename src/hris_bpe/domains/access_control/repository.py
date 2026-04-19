from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from hris_bpe.common.helpers import utc_now
from hris_bpe.domains.access_control.models import (
    AccessControlAuditLog,
    Permission,
    Role,
    RolePermission,
    User,
    UserScopeAccess,
    UserRole,
)


class AccessControlRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_users(self) -> list[User]:
        return list(self.db.execute(select(User).order_by(User.email)).scalars())

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def get_user(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_user_by_login(self, identifier: str) -> User | None:
        statement = select(User).where(
            (User.email == identifier.lower()) | (User.username == identifier)
        )
        return self.db.execute(statement).scalar_one_or_none()

    def list_roles(self, company_ids: set[int] | None = None) -> list[Role]:
        statement = select(Role).order_by(Role.code)
        if company_ids:
            statement = statement.where(Role.company_id.in_(company_ids))
        return list(self.db.execute(statement).scalars())

    def get_roles_by_ids(self, role_ids: list[int]) -> list[Role]:
        if not role_ids:
            return []
        return list(self.db.execute(select(Role).where(Role.id.in_(role_ids))).scalars())

    def list_permissions(self) -> list[Permission]:
        return list(self.db.execute(select(Permission).order_by(Permission.code)).scalars())

    def assign_roles(self, user_id: int, role_ids: list[int]) -> None:
        self.db.execute(delete(UserRole).where(UserRole.user_id == user_id))
        for role_id in role_ids:
            self.db.add(UserRole(user_id=user_id, role_id=role_id))
        self.db.flush()

    def list_roles_for_user(self, user_id: int) -> list[Role]:
        statement = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .order_by(Role.code)
        )
        return list(self.db.execute(statement).scalars())

    def list_permissions_for_user(self, user_id: int) -> list[Permission]:
        statement = (
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user_id)
            .distinct()
            .order_by(Permission.code)
        )
        return list(self.db.execute(statement).scalars())

    def set_last_login(self, user: User) -> None:
        user.last_login_at = utc_now()
        self.db.flush()

    def list_scopes_for_user(self, user_id: int) -> list[UserScopeAccess]:
        statement = (
            select(UserScopeAccess)
            .where(UserScopeAccess.user_id == user_id)
            .order_by(UserScopeAccess.scope_type, UserScopeAccess.id)
        )
        return list(self.db.execute(statement).scalars())

    def replace_scopes(
        self,
        user_id: int,
        scopes: list[UserScopeAccessCreatePayload],
        actor_user_id: int | None = None,
    ) -> list[UserScopeAccess]:
        self.db.execute(delete(UserScopeAccess).where(UserScopeAccess.user_id == user_id))
        items: list[UserScopeAccess] = []
        for scope in scopes:
            item = UserScopeAccess(
                user_id=user_id,
                scope_type=scope.scope_type,
                company_id=scope.company_id,
                branch_id=scope.branch_id,
                client_site_id=scope.client_site_id,
                created_by=actor_user_id,
                updated_by=actor_user_id,
            )
            self.db.add(item)
            items.append(item)
        self.db.flush()
        return items

    def create_audit_log(self, item: AccessControlAuditLog) -> AccessControlAuditLog:
        self.db.add(item)
        self.db.flush()
        return item

    def list_audit_logs(
        self,
        *,
        target_user_id: int | None = None,
        action_type: str | None = None,
    ) -> list[AccessControlAuditLog]:
        statement = select(AccessControlAuditLog).order_by(
            AccessControlAuditLog.created_at.desc(),
            AccessControlAuditLog.id.desc(),
        )
        if target_user_id is not None:
            statement = statement.where(AccessControlAuditLog.target_user_id == target_user_id)
        if action_type is not None:
            statement = statement.where(AccessControlAuditLog.action_type == action_type)
        return list(self.db.execute(statement).scalars())


class UserScopeAccessCreatePayload:
    def __init__(
        self,
        *,
        scope_type: str,
        company_id: int | None = None,
        branch_id: int | None = None,
        client_site_id: int | None = None,
    ) -> None:
        self.scope_type = scope_type
        self.company_id = company_id
        self.branch_id = branch_id
        self.client_site_id = client_site_id
