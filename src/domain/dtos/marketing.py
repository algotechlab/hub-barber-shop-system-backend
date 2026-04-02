from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from src.domain.dtos.schedule import ScheduleOutDTO


class MessageTemplateDTO(BaseModel):
    template: str = ''


class WhatsappConnectionDTO(BaseModel):
    state: str
    qr_base64: str | None = None
    source: Literal['api'] = 'api'


class TemplateMarketingRecordDTO(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    description: str
    context_template: dict
    is_active: bool


class InactiveClientUserDTO(BaseModel):
    id: UUID
    name: str
    email: str
    phone: str
    company_id: UUID
    is_active: bool
    last_visit_at: datetime | None
    days_since_last_visit: int


class InactiveClientsPayloadDTO(BaseModel):
    users: list[InactiveClientUserDTO]
    schedules: list[ScheduleOutDTO]
