from uuid import UUID

from src.domain.dtos.market_paid import MarketPaidCreateDTO
from src.domain.use_case.market_paid import MarketPaidUseCase
from src.interface.api.v1.schema.market_paid import (
    MarketPaidCreateSchema,
    MarketPaidOutSchema,
    PreapprovalPlanSearchResponseSchema,
)


class MarketPaidController:
    def __init__(self, market_paid_use_case: MarketPaidUseCase) -> None:
        self.market_paid_use_case = market_paid_use_case

    async def search_preapproval_plans(
        self, company_id: UUID, offset: int = 0, limit: int = 10
    ) -> PreapprovalPlanSearchResponseSchema:
        response = await self.market_paid_use_case.search_preapproval_plans(
            company_id=company_id, offset=offset, limit=limit
        )
        return PreapprovalPlanSearchResponseSchema.model_validate(response.model_dump())

    async def create_market_paid(
        self, market_paid: MarketPaidCreateSchema
    ) -> MarketPaidOutSchema:
        market_paid_dto = MarketPaidCreateDTO(**market_paid.model_dump())
        response = await self.market_paid_use_case.create_market_paid(market_paid_dto)
        return MarketPaidOutSchema(**response.model_dump())

    async def get_market_paid(self, id: UUID) -> MarketPaidOutSchema:
        response = await self.market_paid_use_case.get_market_paid(id)
        return MarketPaidOutSchema(**response.model_dump())
