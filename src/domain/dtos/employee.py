from datetime import datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator

JOURNEY_MIN_TIME = time(8, 30)
JOURNEY_MAX_TIME = time(21, 0)


def _clock_in_journey_bounds(t: time, field_label: str) -> None:
    if t < JOURNEY_MIN_TIME or t > JOURNEY_MAX_TIME:
        raise ValueError(
            f'O horário de {field_label} da jornada deve estar entre 08:30 e 21:00.'
        )


def validate_employee_journey_pair(start_time: time, end_time: time) -> None:
    _clock_in_journey_bounds(start_time, 'início')
    _clock_in_journey_bounds(end_time, 'fim')
    if start_time >= end_time:
        raise ValueError(
            'O horário de início da jornada deve ser anterior ao horário de fim.'
        )


def validate_employee_journey_partial(
    start_time: Optional[time],
    end_time: Optional[time],
) -> None:
    if start_time is not None:
        _clock_in_journey_bounds(start_time, 'início')
    if end_time is not None:
        _clock_in_journey_bounds(end_time, 'fim')
    if start_time is not None and end_time is not None:
        if start_time >= end_time:
            raise ValueError(
                'O horário de início da jornada deve ser anterior ao horário de fim.'
            )


class EmployeeBaseDTO(BaseModel):
    name: str
    last_name: str
    phone: str
    password: str
    is_active: bool
    role: str
    company_id: UUID
    start_time: time
    end_time: time

    @model_validator(mode='after')
    def _validate_journey(self):
        validate_employee_journey_pair(self.start_time, self.end_time)
        return self


class EmployeeOutDTO(BaseModel):
    id: UUID
    name: str
    last_name: str
    phone: str
    is_active: bool
    role: str
    company_id: UUID
    start_time: time
    end_time: time
    is_block: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}


class UpdateEmployeeDTO(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    company_id: Optional[UUID] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    @model_validator(mode='after')
    def _validate_journey(self):
        validate_employee_journey_partial(self.start_time, self.end_time)
        return self
