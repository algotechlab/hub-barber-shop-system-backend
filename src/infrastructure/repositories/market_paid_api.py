from src.domain.dtos.market_paid import PreapprovalPlanSearchResponseDTO
from src.domain.repositories.market_paid import MarketPaidRepository
from src.infrastructure.external_apis.market_paid import MarketPaidApi


class MarketPaidRepositoryApi(MarketPaidRepository):
    """Implementação do repositório que usa a API Mercado Pago."""

    def __init__(self) -> None:
        self._api = MarketPaidApi()

    async def search_preapproval_plans(
        self, offset: int = 0, limit: int = 10
    ) -> PreapprovalPlanSearchResponseDTO:
        return await self._api.search_preapproval_plans(offset=offset, limit=limit)
