from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateScheduleSchema(BaseModel):
    user_id: UUID
    service_id: UUID
    product_id: UUID
    employee_id: UUID
    time_register: datetime
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    status: bool
    is_canceled: bool


class UpdateScheduleSchema(BaseModel):
    user_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    time_register: Optional[datetime] = None
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    status: Optional[bool] = None
    is_canceled: Optional[bool] = None


class ScheduleOutSchema(BaseModel):
    id: UUID
    user_id: UUID
    service_id: UUID
    product_id: UUID
    employee_id: UUID
    company_id: UUID
    time_register: datetime
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    status: bool
    is_canceled: bool
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    user_name: Optional[str] = None
    employee_name: Optional[str] = None
    service_name: Optional[str] = None
    product_name: Optional[str] = None
    schedule_duration_minutes: Optional[int] = None


class SlotsInSchema(BaseModel):
    employee_id: UUID
    work_start: datetime
    work_end: datetime
    slot_minutes: int = 30
    target_date: Optional[date] = None


class SlotOutSchema(BaseModel):
    id: UUID
    time_start: datetime
    time_end: datetime
    is_available: bool
    is_blocked: bool
