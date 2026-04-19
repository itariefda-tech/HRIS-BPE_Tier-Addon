from __future__ import annotations

from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict


class EmployeeDeploymentCreateRequest(BaseModel):
    employee_id: int
    client_id: int
    client_contract_id: int
    client_site_id: int
    site_post_id: int | None = None
    position_id: int | None = None
    start_date: date
    end_date: date | None = None
    deployment_status: str = "ACTIVE"
    source_type: str | None = None
    notes: str | None = None


class EmployeeDeploymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    client_id: int
    client_contract_id: int
    client_site_id: int
    site_post_id: int | None
    position_id: int | None
    start_date: date
    end_date: date | None
    deployment_status: str
    source_type: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class DeploymentHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_deployment_id: int
    action_type: str
    old_client_site_id: int | None
    new_client_site_id: int | None
    old_site_post_id: int | None
    new_site_post_id: int | None
    action_date: date
    remarks: str | None
    created_by: int | None
    created_at: datetime


class ShiftTypeCreateRequest(BaseModel):
    company_id: int
    code: str
    name: str
    start_time: time
    end_time: time
    cross_day_flag: bool = False
    break_minutes: int = 0
    tolerance_late_minutes: int = 0
    overtime_after_minutes: int = 480


class ShiftTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    code: str
    name: str
    start_time: time
    end_time: time
    cross_day_flag: bool
    break_minutes: int
    tolerance_late_minutes: int
    overtime_after_minutes: int
    created_at: datetime
    updated_at: datetime


class WorkScheduleCreateRequest(BaseModel):
    employee_deployment_id: int
    shift_type_id: int
    scheduled_date: date
    scheduled_start_datetime: datetime | None = None
    scheduled_end_datetime: datetime | None = None
    schedule_status: str = "DRAFT"
    replacement_for_schedule_id: int | None = None


class BulkScheduleGenerateRequest(BaseModel):
    employee_deployment_ids: list[int]
    shift_type_id: int
    date_from: date
    date_to: date
    schedule_status: str = "DRAFT"


class WorkScheduleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    employee_deployment_id: int
    client_site_id: int
    site_post_id: int | None
    shift_type_id: int
    scheduled_date: date
    scheduled_start_datetime: datetime
    scheduled_end_datetime: datetime
    schedule_status: str
    replacement_for_schedule_id: int | None
    generated_by: int | None
    approved_by: int | None
    created_at: datetime
    updated_at: datetime


class EndDeploymentRequest(BaseModel):
    end_date: date
    notes: str | None = None


class WorkScheduleTransitionRequest(BaseModel):
    remarks: str | None = None
