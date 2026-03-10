from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class ScheduleBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    service_id: UUID
    product_id: Optional[UUID] = None
    employee_id: UUID
    company_id: UUID
    time_register: datetime
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    is_confirmed: bool = Field(validation_alias=AliasChoices('is_confirmed', 'status'))
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
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    user_name: Optional[str] = None
    employee_name: Optional[str] = None
    service_name: Optional[str] = None
    product_name: Optional[str] = None
    schedule_duration_minutes: Optional[int] = None


class ScheduleCreateDTO(ScheduleBaseDTO):
    user_id: UUID
    service_id: UUID
    product_id: UUID
    employee_id: UUID
    company_id: UUID
    time_register: datetime
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    is_confirmed: bool = Field(
        default=False, validation_alias=AliasChoices('is_confirmed', 'status')
    )
    is_canceled: bool = False


class ScheduleUpdateDTO(ScheduleBaseDTO):
    user_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    company_id: Optional[UUID] = None
    time_register: Optional[datetime] = None
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    is_confirmed: Optional[bool] = Field(
        default=None, validation_alias=AliasChoices('is_confirmed', 'status')
    )
    is_canceled: Optional[bool] = None


class SlotsInDTO(BaseModel):
    company_id: UUID
    employee_id: UUID
    work_start: datetime
    work_end: datetime
    slot_minutes: int = 30
    target_date: Optional[date] = None


class SlotOutDTO(BaseModel):
    id: UUID
    time_start: datetime
    time_end: datetime
    is_available: bool
    is_blocked: bool
