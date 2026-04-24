from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.user_subscription import (
    UserSubscriptionCreateDTO,
    UserSubscriptionOutDTO,
    UserSubscriptionWithPlanAndClientOutDTO,
    UserSubscriptionWithPlanOutDTO,
)
from src.domain.repositories.user_subscription import UserSubscriptionRepository


class UserSubscriptionService:
    def __init__(self, repository: UserSubscriptionRepository):
        self.repository = repository

    async def create(self, data: UserSubscriptionCreateDTO) -> UserSubscriptionOutDTO:
        return await self.repository.create(data)

    async def get_by_id(
        self, subscription_id: UUID, company_id: UUID
    ) -> Optional[UserSubscriptionOutDTO]:
        return await self.repository.get_by_id(subscription_id, company_id)

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

    async def has_pending_for_plan(
        self, user_id: UUID, subscription_plan_id: UUID, company_id: UUID
    ) -> bool:
        return await self.repository.has_pending_for_plan(
            user_id, subscription_plan_id, company_id
        )

    async def list_pending_by_company(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        client_name: str | None = None,
    ) -> List[UserSubscriptionWithPlanAndClientOutDTO]:
        return await self.repository.list_pending_by_company(
            pagination, company_id, client_name=client_name
        )

    async def activate_pending(
        self,
        subscription_id: UUID,
        company_id: UUID,
        *,
        external_subscription_id: str | None = None,
        payment_method: str,
        payment_at: datetime | None = None,
    ) -> UserSubscriptionOutDTO | None:
        return await self.repository.activate_pending(
            subscription_id,
            company_id,
            external_subscription_id=external_subscription_id,
            payment_method=payment_method,
            payment_at=payment_at,
        )
