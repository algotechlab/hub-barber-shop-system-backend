from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.market_paid import (
    MarketPaidCreateDTO,
    MarketPaidOutDTO,
    PreapprovalPlanSearchResponseDTO,
)
from src.domain.repositories.market_paid import MarketPaidRepository
from src.infrastructure.database.models.market_paid import MarketPaid


class MarketPaidRepositoryPostgres(MarketPaidRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search_preapproval_plans(
        self, company_id: UUID, offset: int = 0, limit: int = 10
    ) -> PreapprovalPlanSearchResponseDTO:
        raise NotImplementedError(
            'search_preapproval_plans deve usar MarketPaidRepositoryApi'
        )

    async def get_market_paid_by_company_id(self, company_id: UUID) -> MarketPaidOutDTO:
        try:
            query = select(MarketPaid).where(
                MarketPaid.company_id.__eq__(company_id),
                MarketPaid.is_deleted.__eq__(False),
            )
            result = await self.session.execute(query)
            market_paid = result.scalar_one_or_none()
            if market_paid is None:
                return None
            return MarketPaidOutDTO.model_validate(market_paid, from_attributes=True)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def create_market_paid(
        self, market_paid: MarketPaidCreateDTO
    ) -> MarketPaidOutDTO:
        try:
            market_paid = MarketPaid(**market_paid.model_dump())
            self.session.add(market_paid)
            await self.session.commit()
            await self.session.refresh(market_paid)
            return MarketPaidOutDTO.model_validate(market_paid, from_attributes=True)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_market_paid(self, id: UUID) -> MarketPaidOutDTO:
        try:
            query = select(MarketPaid).where(MarketPaid.id.__eq__(id))
            result = await self.session.execute(query)
            market_paid = result.scalar_one_or_none()
            if market_paid is None:
                return None
            return MarketPaidOutDTO.model_validate(market_paid, from_attributes=True)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
