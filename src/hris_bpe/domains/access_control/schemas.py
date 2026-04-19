from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    module_name: str
    created_at: datetime


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    code: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class UserCreateRequest(BaseModel):
    employee_id: int | None = None
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=8, max_length=128)
    role_ids: list[int] = Field(default_factory=list)
    is_active: bool = True


class AssignRolesRequest(BaseModel):
    role_ids: list[int] = Field(default_factory=list)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int | None
    username: str
    email: EmailStr
    phone: str | None
    last_login_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role_codes: list[str] = Field(default_factory=list)


class UserScopeAccessCreateRequest(BaseModel):
    scope_type: str
    company_id: int | None = None
    branch_id: int | None = None
    client_site_id: int | None = None


class UserScopeAccessRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    scope_type: str
    company_id: int | None
    branch_id: int | None
    client_site_id: int | None
    created_at: datetime
    updated_at: datetime


class AccessControlAuditLogRead(BaseModel):
    id: int
    actor_user_id: int
    target_user_id: int
    action_type: str
    entity_name: str
    old_data: Any
    new_data: Any
    remarks: str | None
    created_at: datetime
