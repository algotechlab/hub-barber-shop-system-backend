from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.interface.api.v1.schema.schedule import ScheduleOutSchema


class MessageTemplateOutSchema(BaseModel):
    template: str = ''


class MessageTemplatePutSchema(BaseModel):
    template: str = Field(..., min_length=0)


class WhatsappConnectionOutSchema(BaseModel):
    state: str
    status: str | None = None
    qr_base64: str | None = None
    source: str = 'api'


class SendMarketingMessageSchema(BaseModel):
    number: str = Field(..., description='Telefone com DDI, ex: 5511999999999')
    text: str | None = Field(
        None, description='Texto opcional; se omitido, usa o template salvo'
    )


class InactiveClientUserOutSchema(BaseModel):
    id: UUID
    name: str
    email: str
    phone: str
    company_id: UUID
    is_active: bool
    last_visit_at: datetime | None
    days_since_last_visit: int = Field(
        ...,
        description='Dias desde o último agendamento concluído (não cancelado); '
        'se nunca houve, usa a data de cadastro como referência.',
    )


class InactiveClientsOutSchema(BaseModel):
    users: list[InactiveClientUserOutSchema]
    schedules: list[ScheduleOutSchema]
