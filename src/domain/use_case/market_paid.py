from uuid import UUID

from src.domain.dtos.market_paid import (
    MarketPaidCreateDTO,
    MarketPaidOutDTO,
    PreapprovalPlanSearchResponseDTO,
)
from src.domain.service.market_paid import MarketPaidService


class MarketPaidUseCase:
    def __init__(self, market_paid_service: MarketPaidService) -> None:
        self.market_paid_service = market_paid_service

    async def search_preapproval_plans(
        self, company_id: UUID, offset: int = 0, limit: int = 10
    ) -> PreapprovalPlanSearchResponseDTO:
        return await self.market_paid_service.search_preapproval_plans(
            company_id=company_id, offset=offset, limit=limit
        )

    async def create_market_paid(
        self, market_paid: MarketPaidCreateDTO
    ) -> MarketPaidOutDTO:
        return await self.market_paid_service.create_market_paid(market_paid)

    async def get_market_paid(self, id: UUID) -> MarketPaidOutDTO:
        return await self.market_paid_service.get_market_paid(id)
