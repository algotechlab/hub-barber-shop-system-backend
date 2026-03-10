from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.dtos.market_paid import (
    MarketPaidCreateDTO,
    MarketPaidOutDTO,
    PreapprovalPlanSearchResponseDTO,
)


class MarketPaidRepository(ABC):
    @abstractmethod
    async def search_preapproval_plans(
        self, company_id: UUID, offset: int = 0, limit: int = 10
    ) -> PreapprovalPlanSearchResponseDTO: ...

    @abstractmethod
    async def create_market_paid(
        self, market_paid: MarketPaidCreateDTO
    ) -> MarketPaidOutDTO: ...

    @abstractmethod
    async def get_market_paid(self, id: UUID) -> MarketPaidOutDTO: ...
