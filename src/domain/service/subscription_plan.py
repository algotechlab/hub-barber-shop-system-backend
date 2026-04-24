from typing import List, Optional
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.subscription_plan import (
    SubscriptionPlanCreateDTO,
    SubscriptionPlanOutDTO,
    SubscriptionPlanUpdateDTO,
)
from src.domain.repositories.subscription_plan import SubscriptionPlanRepository


class SubscriptionPlanService:
    def __init__(self, repository: SubscriptionPlanRepository):
        self.repository = repository

    async def create_plan(
        self, data: SubscriptionPlanCreateDTO
    ) -> SubscriptionPlanOutDTO:
        return await self.repository.create_plan(data)

    async def get_plan(
        self,
        id: UUID,
        company_id: UUID,
        *,
        active_only: bool = False,
    ) -> Optional[SubscriptionPlanOutDTO]:
        return await self.repository.get_plan(id, company_id, active_only=active_only)

    async def list_plans(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        *,
        active_only: bool = False,
    ) -> List[SubscriptionPlanOutDTO]:
        return await self.repository.list_plans(
            pagination, company_id, active_only=active_only
        )

    async def update_plan(
        self, id: UUID, data: SubscriptionPlanUpdateDTO, company_id: UUID
    ) -> Optional[SubscriptionPlanOutDTO]:
        return await self.repository.update_plan(id, data, company_id)

    async def delete_plan(self, id: UUID, company_id: UUID) -> bool:
        return await self.repository.delete_plan(id, company_id)

    async def service_belongs_to_company(
        self, service_id: UUID, company_id: UUID
    ) -> bool:
        return await self.repository.service_belongs_to_company(service_id, company_id)
