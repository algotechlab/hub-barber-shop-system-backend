from uuid import UUID

from src.domain.dtos.marketing import (
    InactiveClientsPayloadDTO,
    MessageTemplateDTO,
    WhatsappConnectionDTO,
)
from src.domain.service.marketing import MarketingService


class MarketingUseCase:
    def __init__(self, marketing_service: MarketingService):
        self._service = marketing_service

    async def get_message_template(self, company_id: UUID) -> MessageTemplateDTO:
        return await self._service.get_message_template(company_id)

    async def save_message_template(
        self, company_id: UUID, text: str
    ) -> MessageTemplateDTO:
        return await self._service.save_message_template(company_id, text)

    async def get_whatsapp_connection(self, company_id: UUID) -> WhatsappConnectionDTO:
        return await self._service.get_whatsapp_connection(company_id)

    async def get_inactive_clients(
        self,
        company_id: UUID,
        *,
        email: str | None = None,
        min_days: int | None = None,
        max_days: int | None = None,
        lookback_years: int = 2,
        schedules_limit: int = 3000,
    ) -> InactiveClientsPayloadDTO:
        return await self._service.get_inactive_clients(
            company_id,
            email=email,
            min_days=min_days,
            max_days=max_days,
            lookback_years=lookback_years,
            schedules_limit=schedules_limit,
        )

    async def send_template_message(
        self, company_id: UUID, number: str, override_text: str | None = None
    ) -> None:
        await self._service.send_template_message(
            company_id, number, override_text=override_text
        )
