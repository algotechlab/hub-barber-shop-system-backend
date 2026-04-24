from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.subscription_plan import (
    SubscriptionPlanCreateDTO,
    SubscriptionPlanUpdateDTO,
)
from src.domain.use_case.subscription_plan import SubscriptionPlanUseCase
from src.interface.api.v1.schema.subscription_plan import (
    CreateSubscriptionPlanSchema,
    SubscriptionPlanOutSchema,
    UpdateSubscriptionPlanSchema,
)


class SubscriptionPlanController:
    def __init__(self, use_case: SubscriptionPlanUseCase):
        self._use_case = use_case

    async def list_plans(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        *,
        active_only: bool,
    ) -> list[SubscriptionPlanOutSchema]:
        rows = await self._use_case.list_plans(
            pagination, company_id, active_only=active_only
        )
        return [SubscriptionPlanOutSchema(**r.model_dump()) for r in rows]

    async def create_plan(
        self, body: CreateSubscriptionPlanSchema, company_id: UUID
    ) -> SubscriptionPlanOutSchema:
        dto = SubscriptionPlanCreateDTO(
            **body.model_dump(),
            company_id=company_id,
        )
        out = await self._use_case.create_plan(dto)
        return SubscriptionPlanOutSchema(**out.model_dump())

    async def get_plan(
        self, plan_id: UUID, company_id: UUID, *, active_only: bool
    ) -> SubscriptionPlanOutSchema:
        out = await self._use_case.get_plan(
            plan_id, company_id, active_only=active_only
        )
        return SubscriptionPlanOutSchema(**out.model_dump())

    async def update_plan(
        self,
        plan_id: UUID,
        body: UpdateSubscriptionPlanSchema,
        company_id: UUID,
    ) -> SubscriptionPlanOutSchema:
        dto = SubscriptionPlanUpdateDTO(
            **body.model_dump(exclude_unset=True),
        )
        out = await self._use_case.update_plan(plan_id, dto, company_id)
        return SubscriptionPlanOutSchema(**out.model_dump())

    async def delete_plan(self, plan_id: UUID, company_id: UUID) -> None:
        await self._use_case.delete_plan(plan_id, company_id)
