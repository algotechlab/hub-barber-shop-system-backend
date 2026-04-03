from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator

from src.domain.dtos.employee import (
    validate_employee_journey_pair,
    validate_employee_journey_partial,
)


class EmployeeSchema(BaseModel):
    id: UUID
    name: str
    last_name: str
    phone: str
    is_active: bool
    role: str
    company_id: UUID
    start_time: datetime
    end_time: datetime
    is_block: bool = False


class EmployeeOutSchema(BaseModel):
    id: UUID
    name: str
    last_name: str
    phone: str
    is_active: bool
    role: str
    company_id: UUID
    start_time: datetime
    end_time: datetime
    created_at: datetime
    updated_at: datetime


class CreateEmployeeSchema(BaseModel):
    name: str
    last_name: str
    phone: str
    password: str
    is_active: bool
    role: str
    start_time: datetime
    end_time: datetime

    @model_validator(mode='after')
    def _validate_journey(self):
        validate_employee_journey_pair(self.start_time, self.end_time)
        return self


class UpdateEmployeeSchema(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    company_id: Optional[UUID] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @model_validator(mode='after')
    def _validate_journey(self):
        validate_employee_journey_partial(self.start_time, self.end_time)
        return self
