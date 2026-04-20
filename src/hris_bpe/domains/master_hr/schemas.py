from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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

    @field_validator("employee_number")
    @classmethod
    def normalize_employee_number(cls, value: str) -> str:
        return value.strip().upper()


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


class EmployeeBatchImportRequest(BaseModel):
    employees: list[EmployeeCreateRequest] = Field(min_length=1)
    stop_on_error: bool = False


class EmployeeBatchImportItemRead(BaseModel):
    row_no: int
    status: str
    employee_number: str
    company_id: int
    full_name: str
    message: str
    employee: EmployeeRead | None = None


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

    @field_validator("guard_registration_number")
    @classmethod
    def normalize_guard_registration_number(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        return normalized or None


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

    @field_validator("contract_number")
    @classmethod
    def normalize_contract_number(cls, value: str) -> str:
        return value.strip().upper()


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


class EmployeeEmergencyContactCreateRequest(BaseModel):
    contact_name: str = Field(min_length=2, max_length=180)
    relationship_type: str = Field(min_length=2, max_length=80)
    phone: str = Field(min_length=6, max_length=30)
    alternate_phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    is_primary: bool = False
    notes: str | None = None


class EmployeeEmergencyContactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    contact_name: str
    relationship_type: str
    phone: str
    alternate_phone: str | None
    email: EmailStr | None
    address: str | None
    is_primary: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime


class EmployeeDocumentCreateRequest(BaseModel):
    document_type: str = Field(min_length=2, max_length=80)
    document_name: str = Field(min_length=2, max_length=180)
    file_path: str = Field(min_length=3, max_length=255)
    document_number: str | None = None
    issued_date: date | None = None
    expiry_date: date | None = None
    active_flag: bool = True
    notes: str | None = None


class EmployeeDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    document_type: str
    document_name: str
    file_path: str
    document_number: str | None
    issued_date: date | None
    expiry_date: date | None
    active_flag: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime


class EmployeeLifecycleEventCreateRequest(BaseModel):
    action_type: str = Field(min_length=2, max_length=40)
    effective_date: date
    new_employee_status: str | None = None
    new_employment_status: str | None = None
    new_branch_id: int | None = None
    new_department_id: int | None = None
    new_position_id: int | None = None
    remarks: str | None = None

    @field_validator("action_type")
    @classmethod
    def normalize_action_type(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("new_employee_status", "new_employment_status")
    @classmethod
    def normalize_status_values(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        return normalized or None


class EmployeeLifecycleEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    action_type: str
    effective_date: date
    old_employee_status: str | None
    new_employee_status: str | None
    old_employment_status: str | None
    new_employment_status: str | None
    old_branch_id: int | None
    new_branch_id: int | None
    old_department_id: int | None
    new_department_id: int | None
    old_position_id: int | None
    new_position_id: int | None
    old_hire_date: date | None
    new_hire_date: date | None
    old_resign_date: date | None
    new_resign_date: date | None
    remarks: str | None
    created_at: datetime
    updated_at: datetime


class EmployeeLifecycleTransitionRead(BaseModel):
    event: EmployeeLifecycleEventRead
    employee: EmployeeRead
