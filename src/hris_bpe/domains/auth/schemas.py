from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=3)
    password: str = Field(min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=32)


class AuthenticatedUser(BaseModel):
    id: int
    employee_id: int | None
    username: str
    email: EmailStr
    phone: str | None
    is_active: bool
    last_login_at: datetime | None
    role_codes: list[str]
    permission_codes: list[str]
    company_ids: list[int]
    company_scope_ids: list[int] = []
    branch_scope_ids: list[int] = []
    site_scope_ids: list[int] = []
    has_explicit_scope: bool = False


class TokenBundleResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    session_id: str
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime


class LoginResponse(TokenBundleResponse):
    user: AuthenticatedUser


class RefreshTokenResponse(TokenBundleResponse):
    user: AuthenticatedUser


class LogoutResponse(BaseModel):
    revoked_access_token_jti: str
    revoked_session_id: str | None
