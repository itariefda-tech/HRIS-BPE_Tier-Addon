from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ClientSiteCreateRequest(BaseModel):
    client_id: int
    code: str
    name: str
    address: str | None = None
    city: str | None = None
    province: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    radius_meters: int | None = None
    status: str = "ACTIVE"


class ClientSiteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    code: str
    name: str
    address: str | None
    city: str | None
    province: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    radius_meters: int | None
    status: str
    created_at: datetime
    updated_at: datetime


class SitePostCreateRequest(BaseModel):
    client_site_id: int
    code: str
    name: str
    description: str | None = None
    active_flag: bool = True


class SitePostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_site_id: int
    code: str
    name: str
    description: str | None
    active_flag: bool
    created_at: datetime
    updated_at: datetime

