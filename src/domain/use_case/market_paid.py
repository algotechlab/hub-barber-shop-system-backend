from src.domain.dtos.market_paid import PreapprovalPlanSearchResponseDTO
from src.domain.service.market_paid import MarketPaidService


class MarketPaidUseCase:
    def __init__(self, market_paid_service: MarketPaidService) -> None:
        self.market_paid_service = market_paid_service

    async def search_preapproval_plans(
        self, offset: int = 0, limit: int = 10
    ) -> PreapprovalPlanSearchResponseDTO:
        return await self.market_paid_service.search_preapproval_plans(
            offset=offset, limit=limit
        )
