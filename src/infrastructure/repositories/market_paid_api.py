from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import NotFoundException
from src.domain.dtos.market_paid import (
    MarketPaidCreateDTO,
    MarketPaidOutDTO,
    PreapprovalPlanSearchResponseDTO,
)
from src.domain.repositories.market_paid import MarketPaidRepository
from src.infrastructure.external_apis.market_paid import MarketPaidApi
from src.infrastructure.repositories.market_paid_postgres import (
    MarketPaidRepositoryPostgres,
)


class MarketPaidRepositoryApi(MarketPaidRepository):
    """Implementação do repositório que usa a API Mercado Pago."""

    def __init__(self, session: AsyncSession) -> None:
        self._api = MarketPaidApi()
        self._postgres = MarketPaidRepositoryPostgres(session)

    async def search_preapproval_plans(
        self, company_id: UUID, offset: int = 0, limit: int = 10
    ) -> PreapprovalPlanSearchResponseDTO:
        market_paid = await self._postgres.get_market_paid_by_company_id(company_id)
        if market_paid is None:
            raise NotFoundException(
                f'Credenciais do Mercado Pago não encontradas '
                f'para a empresa {company_id}.'
            )

        access_token = market_paid.market_paid_acess_token or market_paid.access_token
        return await self._api.search_preapproval_plans(
            access_token=access_token,
            offset=offset,
            limit=limit,
        )

    async def create_market_paid(
        self, market_paid: MarketPaidCreateDTO
    ) -> MarketPaidOutDTO:
        return await self._postgres.create_market_paid(market_paid)

    async def get_market_paid(self, id: UUID) -> MarketPaidOutDTO:
        return await self._postgres.get_market_paid(id)
