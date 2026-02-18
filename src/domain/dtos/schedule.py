from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class ScheduleBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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

    @field_validator('time_register', 'time_start', 'time_end', mode='after')
    @classmethod
    def _normalize_datetimes(cls, value: Optional[datetime]) -> Optional[datetime]:
        """
        Normaliza datetimes timezone-aware para UTC sem tzinfo.

        Motivo: no Postgres estamos usando TIMESTAMP WITHOUT TIME ZONE.
        Se vier timezone-aware (ex: 2026-02-14T20:06:18Z),
        o driver asyncpg pode falhar ao bindar o valor.
        """
        if value is None:
            return None
        if isinstance(value, datetime) and value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value


class ScheduleOutDTO(ScheduleBaseDTO):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool


class ScheduleCreateDTO(ScheduleBaseDTO):
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


class ScheduleUpdateDTO(ScheduleBaseDTO):
    user_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    company_id: Optional[UUID] = None
    time_register: Optional[datetime] = None
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    status: Optional[bool] = None
    is_canceled: Optional[bool] = None
