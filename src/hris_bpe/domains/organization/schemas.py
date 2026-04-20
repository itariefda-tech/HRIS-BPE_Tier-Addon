from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from hris_bpe.domains.auth.schemas import PreferredLanguage, PreferredTheme


def _normalize_optional_preference(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().lower()


class CompanyCreateRequest(BaseModel):
    code: str = Field(min_length=2, max_length=60)
    name: str = Field(min_length=2, max_length=150)
    legal_name: str | None = None
    tax_number: str | None = None
    address: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    default_language: PreferredLanguage | None = None
    default_theme: PreferredTheme | None = None
    status: str = "ACTIVE"

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("default_language", "default_theme", mode="before")
    @classmethod
    def normalize_preferences(cls, value: str | None) -> str | None:
        return _normalize_optional_preference(value)


class CompanySettingsUpdateRequest(BaseModel):
    default_language: PreferredLanguage | None = None
    default_theme: PreferredTheme | None = None

    @field_validator("default_language", "default_theme", mode="before")
    @classmethod
    def normalize_preferences(cls, value: str | None) -> str | None:
        return _normalize_optional_preference(value)


class CompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    legal_name: str | None
    tax_number: str | None
    address: str | None
    phone: str | None
    email: EmailStr | None
    default_language: PreferredLanguage | None
    default_theme: PreferredTheme | None
    status: str
    created_at: datetime
    updated_at: datetime


class BranchCreateRequest(BaseModel):
    company_id: int
    code: str
    name: str
    address: str | None = None
    city: str | None = None
    province: str | None = None
    phone: str | None = None
    status: str = "ACTIVE"

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper()


class BranchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    code: str
    name: str
    address: str | None
    city: str | None
    province: str | None
    phone: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class DepartmentCreateRequest(BaseModel):
    company_id: int
    code: str
    name: str
    description: str | None = None

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper()


class DepartmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    code: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class PositionCreateRequest(BaseModel):
    company_id: int
    code: str
    name: str
    category: str | None = None
    level_order: int = 0
    description: str | None = None

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper()


class PositionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    code: str
    name: str
    category: str | None
    level_order: int
    description: str | None
    created_at: datetime
    updated_at: datetime
