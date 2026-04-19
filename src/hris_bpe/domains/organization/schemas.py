from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CompanyCreateRequest(BaseModel):
    code: str = Field(min_length=2, max_length=60)
    name: str = Field(min_length=2, max_length=150)
    legal_name: str | None = None
    tax_number: str | None = None
    address: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    status: str = "ACTIVE"


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

