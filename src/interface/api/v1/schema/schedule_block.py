from datetime import date, datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator


class CreateScheduleBlockSchema(BaseModel):
    employee_id: UUID
    start_date: date
    end_date: date
    start_time: time
    end_time: time

    @model_validator(mode='after')
    def validate_date_range(self) -> 'CreateScheduleBlockSchema':
        if self.end_date < self.start_date:
            raise ValueError('end_date must be greater than or equal to start_date')
        return self


class ScheduleBlockOutSchema(BaseModel):
    id: UUID
    employee_id: UUID
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    created_at: datetime
    updated_at: datetime


class UpdateScheduleBlockSchema(BaseModel):
    employee_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    @model_validator(mode='after')
    def validate_date_range(self) -> 'UpdateScheduleBlockSchema':
        if self.start_date is not None and self.end_date is not None:
            if self.end_date < self.start_date:
                raise ValueError('end_date must be greater than or equal to start_date')
        return self


class ScheduleBlockOutListSchema(BaseModel):
    id: UUID
    employee_id: Optional[UUID] = None
    employee_name: Optional[str] = None
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    is_block: bool
    created_at: datetime
    updated_at: datetime
