from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class ClientCreateRequest(BaseModel):
    company_id: int
    code: str
    name: str
    industry_type: str | None = None
    contact_person_name: str | None = None
    contact_person_phone: str | None = None
    contact_person_email: EmailStr | None = None
    billing_address: str | None = None
    tax_number: str | None = None
    status: str = "ACTIVE"


class ClientUpdateRequest(BaseModel):
    code: str | None = None
    name: str | None = None
    industry_type: str | None = None
    contact_person_name: str | None = None
    contact_person_phone: str | None = None
    contact_person_email: EmailStr | None = None
    billing_address: str | None = None
    tax_number: str | None = None
    status: str | None = None


class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    code: str
    name: str
    industry_type: str | None
    contact_person_name: str | None
    contact_person_phone: str | None
    contact_person_email: EmailStr | None
    billing_address: str | None
    tax_number: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class ClientContractCreateRequest(BaseModel):
    client_id: int
    contract_number: str
    contract_title: str
    start_date: date
    end_date: date | None = None
    contract_type: str | None = None
    currency: str = "IDR"
    tax_included_flag: bool = True
    payment_term_days: int = 30
    sla_description: str | None = None
    status: str = "ACTIVE"
    notes: str | None = None


class ClientContractRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    contract_number: str
    contract_title: str
    start_date: date
    end_date: date | None
    contract_type: str | None
    currency: str
    tax_included_flag: bool
    payment_term_days: int
    sla_description: str | None
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
