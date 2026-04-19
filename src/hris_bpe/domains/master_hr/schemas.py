from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeCreateRequest(BaseModel):
    company_id: int
    branch_id: int
    department_id: int | None = None
    position_id: int | None = None
    employee_number: str = Field(min_length=2, max_length=80)
    full_name: str = Field(min_length=2, max_length=180)
    nik: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    gender: str | None = None
    marital_status: str | None = None
    hire_date: date | None = None
    employment_status: str | None = None
    employee_status: str = "ACTIVE"
    resign_date: date | None = None
    photo_path: str | None = None


class EmployeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    branch_id: int
    department_id: int | None
    position_id: int | None
    employee_number: str
    full_name: str
    nik: str | None
    email: EmailStr | None
    phone: str | None
    address: str | None
    gender: str | None
    marital_status: str | None
    hire_date: date | None
    employment_status: str | None
    employee_status: str
    resign_date: date | None
    photo_path: str | None
    created_at: datetime
    updated_at: datetime


class GuardProfileCreateRequest(BaseModel):
    employee_id: int
    guard_registration_number: str | None = None
    guard_level: str | None = None
    uniform_size: str | None = None
    shoe_size: str | None = None
    blood_type: str | None = None
    firearm_license_flag: bool = False
    driving_license_type: str | None = None
    fitness_status: str | None = None
    blacklist_flag: bool = False
    blacklist_reason: str | None = None


class GuardProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    guard_registration_number: str | None
    guard_level: str | None
    uniform_size: str | None
    shoe_size: str | None
    blood_type: str | None
    firearm_license_flag: bool
    driving_license_type: str | None
    fitness_status: str | None
    blacklist_flag: bool
    blacklist_reason: str | None
    created_at: datetime
    updated_at: datetime


class EmployeeContractCreateRequest(BaseModel):
    employee_id: int
    contract_number: str
    contract_type: str
    start_date: date
    end_date: date | None = None
    salary_type: str | None = None
    basic_salary: Decimal | None = None
    allowance_fixed: Decimal | None = None
    notes: str | None = None
    status: str = "ACTIVE"


class EmployeeContractRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    contract_number: str
    contract_type: str
    start_date: date
    end_date: date | None
    salary_type: str | None
    basic_salary: Decimal | None
    allowance_fixed: Decimal | None
    notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime

