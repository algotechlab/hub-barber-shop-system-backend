from uuid import UUID

from src.domain.dtos.market_paid import (
    MarketPaidCreateDTO,
    MarketPaidOutDTO,
    PreapprovalPlanSearchResponseDTO,
)
from src.domain.repositories.market_paid import MarketPaidRepository


class MarketPaidService:
    def __init__(self, market_paid_repository: MarketPaidRepository) -> None:
        self.market_paid_repository = market_paid_repository

    async def search_preapproval_plans(
        self, company_id: UUID, offset: int = 0, limit: int = 10
    ) -> PreapprovalPlanSearchResponseDTO:
        return await self.market_paid_repository.search_preapproval_plans(
            company_id=company_id, offset=offset, limit=limit
        )

    async def create_market_paid(
        self, market_paid: MarketPaidCreateDTO
    ) -> MarketPaidOutDTO:
        return await self.market_paid_repository.create_market_paid(market_paid)

    async def get_market_paid(self, id: UUID) -> MarketPaidOutDTO:
        return await self.market_paid_repository.get_market_paid(id)
