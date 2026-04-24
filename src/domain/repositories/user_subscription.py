from abc import ABC, abstractmethod
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


class UserSubscriptionRepository(ABC):
    @abstractmethod
    async def create(
        self, data: UserSubscriptionCreateDTO
    ) -> UserSubscriptionOutDTO: ...

    @abstractmethod
    async def get_by_id(
        self, subscription_id: UUID, company_id: UUID
    ) -> Optional[UserSubscriptionOutDTO]: ...

    @abstractmethod
    async def list_by_user(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        user_id: UUID,
    ) -> List[UserSubscriptionWithPlanOutDTO]: ...

    @abstractmethod
    async def list_pending_by_company(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        client_name: str | None = None,
    ) -> List[UserSubscriptionWithPlanAndClientOutDTO]: ...

    @abstractmethod
    async def has_active_for_plan(
        self, user_id: UUID, subscription_plan_id: UUID, company_id: UUID
    ) -> bool: ...

    @abstractmethod
    async def has_pending_for_plan(
        self, user_id: UUID, subscription_plan_id: UUID, company_id: UUID
    ) -> bool: ...

    @abstractmethod
    async def activate_pending(
        self,
        subscription_id: UUID,
        company_id: UUID,
        *,
        external_subscription_id: str | None = None,
        payment_method: str,
        payment_at: datetime | None = None,
    ) -> Optional[UserSubscriptionOutDTO]: ...
