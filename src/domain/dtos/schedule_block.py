from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ScheduleBlockCreateDTO(BaseModel):
    employee_id: UUID
    company_id: UUID
    start_time: datetime
    end_time: datetime


class ScheduleBlockOutDTO(BaseModel):
    id: UUID
    employee_id: UUID
    company_id: UUID
    start_time: datetime
    end_time: datetime
    is_block: bool
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}


class ScheduleBlockUpdateDTO(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_block: Optional[bool] = None
