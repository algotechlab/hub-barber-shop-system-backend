from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.user_subscription import (
    UserSubscriptionCreateDTO,
    UserSubscriptionOutDTO,
    UserSubscriptionWithPlanOutDTO,
)


class UserSubscriptionRepository(ABC):
    @abstractmethod
    async def create(
        self, data: UserSubscriptionCreateDTO
    ) -> UserSubscriptionOutDTO: ...

    @abstractmethod
    async def list_by_user(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        user_id: UUID,
    ) -> List[UserSubscriptionWithPlanOutDTO]: ...

    @abstractmethod
    async def has_active_for_plan(
        self, user_id: UUID, subscription_plan_id: UUID, company_id: UUID
    ) -> bool: ...
