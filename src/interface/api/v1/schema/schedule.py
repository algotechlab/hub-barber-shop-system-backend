from datetime import datetime
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
