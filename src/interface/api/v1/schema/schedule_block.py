from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateScheduleBlockSchema(BaseModel):
    employee_id: UUID
    start_time: datetime
    end_time: datetime


class ScheduleBlockOutSchema(BaseModel):
    id: UUID
    employee_id: UUID
    start_time: datetime
    end_time: datetime
    created_at: datetime
    updated_at: datetime


class UpdateScheduleBlockSchema(BaseModel):
    employee_id: Optional[UUID] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
