from src.domain.use_case.market_paid import MarketPaidUseCase
from src.interface.api.v1.schema.market_paid import (
    PreapprovalPlanSearchResponseSchema,
)


class MarketPaidController:
    def __init__(self, market_paid_use_case: MarketPaidUseCase) -> None:
        self.market_paid_use_case = market_paid_use_case

    async def search_preapproval_plans(
        self, offset: int = 0, limit: int = 10
    ) -> PreapprovalPlanSearchResponseSchema:
        response = await self.market_paid_use_case.search_preapproval_plans(
            offset=offset, limit=limit
        )
        return PreapprovalPlanSearchResponseSchema.model_validate(response.model_dump())
