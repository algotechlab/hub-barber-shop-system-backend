from abc import abstractmethod

from src.domain.dtos.market_paid import PreapprovalPlanSearchResponseDTO


class MarketPaidRepository:
    @abstractmethod
    async def search_preapproval_plans(
        self, offset: int = 0, limit: int = 10
    ) -> PreapprovalPlanSearchResponseDTO: ...
