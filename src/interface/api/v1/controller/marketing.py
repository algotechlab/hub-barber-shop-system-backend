from uuid import UUID

from src.domain.use_case.marketing import MarketingUseCase
from src.interface.api.v1.schema.marketing import (
    InactiveClientsOutSchema,
    InactiveClientUserOutSchema,
    MessageTemplateOutSchema,
    MessageTemplatePutSchema,
    WhatsappConnectionOutSchema,
)
from src.interface.api.v1.schema.schedule import ScheduleOutSchema


class MarketingController:
    def __init__(self, use_case: MarketingUseCase):
        self._use_case = use_case

    async def get_message_template(self, company_id: UUID) -> MessageTemplateOutSchema:
        dto = await self._use_case.get_message_template(company_id)
        return MessageTemplateOutSchema(template=dto.template)

    async def save_message_template(
        self, company_id: UUID, body: MessageTemplatePutSchema
    ) -> MessageTemplateOutSchema:
        dto = await self._use_case.save_message_template(company_id, body.template)
        return MessageTemplateOutSchema(template=dto.template)

    async def get_whatsapp_connection(
        self, company_id: UUID
    ) -> WhatsappConnectionOutSchema:
        dto = await self._use_case.get_whatsapp_connection(company_id)
        return WhatsappConnectionOutSchema(
            state=dto.state,
            status=dto.state,
            qr_base64=dto.qr_base64,
            source=dto.source,
        )

    async def send_message(
        self, company_id: UUID, number: str, text: str | None
    ) -> None:
        await self._use_case.send_template_message(
            company_id, number, override_text=text
        )

    async def get_inactive_clients(
        self,
        company_id: UUID,
        *,
        email: str | None,
        min_days: int | None,
        max_days: int | None,
        lookback_years: int,
        schedules_limit: int,
    ) -> InactiveClientsOutSchema:
        payload = await self._use_case.get_inactive_clients(
            company_id,
            email=email,
            min_days=min_days,
            max_days=max_days,
            lookback_years=lookback_years,
            schedules_limit=schedules_limit,
        )
        return InactiveClientsOutSchema(
            users=[
                InactiveClientUserOutSchema.model_validate(u.model_dump())
                for u in payload.users
            ],
            schedules=[
                ScheduleOutSchema.model_validate(s.model_dump())
                for s in payload.schedules
            ],
        )
