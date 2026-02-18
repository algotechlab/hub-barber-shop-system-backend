from src.domain.dtos.market_paid import PreapprovalPlanSearchResponseDTO
from src.domain.repositories.market_paid import MarketPaidRepository


class MarketPaidService:
    def __init__(self, market_paid_repository: MarketPaidRepository) -> None:
        self.market_paid_repository = market_paid_repository

    async def search_preapproval_plans(
        self, offset: int = 0, limit: int = 10
    ) -> PreapprovalPlanSearchResponseDTO:
        return await self.market_paid_repository.search_preapproval_plans(
            offset=offset, limit=limit
        )
