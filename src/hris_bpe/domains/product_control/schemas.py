from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ProductTierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class FeatureModuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    module_category: str
    default_tier_id: int | None
    is_add_on: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CompanySubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    product_tier_id: int
    start_date: date
    end_date: date | None
    subscription_status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

