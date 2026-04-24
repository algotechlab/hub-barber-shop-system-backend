from typing import List
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.user_subscription import (
    UserSubscriptionCreateDTO,
    UserSubscriptionOutDTO,
    UserSubscriptionWithPlanOutDTO,
)
from src.domain.repositories.user_subscription import UserSubscriptionRepository


class UserSubscriptionService:
    def __init__(self, repository: UserSubscriptionRepository):
        self.repository = repository

    async def create(self, data: UserSubscriptionCreateDTO) -> UserSubscriptionOutDTO:
        return await self.repository.create(data)

    async def list_by_user(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        user_id: UUID,
    ) -> List[UserSubscriptionWithPlanOutDTO]:
        return await self.repository.list_by_user(pagination, company_id, user_id)

    async def has_active_for_plan(
        self, user_id: UUID, subscription_plan_id: UUID, company_id: UUID
    ) -> bool:
        return await self.repository.has_active_for_plan(
            user_id, subscription_plan_id, company_id
        )
