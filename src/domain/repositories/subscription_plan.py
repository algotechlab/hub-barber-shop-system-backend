from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.subscription_plan import (
    SubscriptionPlanCreateDTO,
    SubscriptionPlanOutDTO,
    SubscriptionPlanUpdateDTO,
)


class SubscriptionPlanRepository(ABC):
    @abstractmethod
    async def create_plan(
        self, data: SubscriptionPlanCreateDTO
    ) -> SubscriptionPlanOutDTO: ...

    @abstractmethod
    async def get_plan(
        self,
        id: UUID,
        company_id: UUID,
        *,
        active_only: bool = False,
    ) -> Optional[SubscriptionPlanOutDTO]: ...

    @abstractmethod
    async def list_plans(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        *,
        active_only: bool = False,
    ) -> List[SubscriptionPlanOutDTO]: ...

    @abstractmethod
    async def update_plan(
        self, id: UUID, data: SubscriptionPlanUpdateDTO, company_id: UUID
    ) -> Optional[SubscriptionPlanOutDTO]: ...

    @abstractmethod
    async def delete_plan(self, id: UUID, company_id: UUID) -> bool: ...

    @abstractmethod
    async def service_belongs_to_company(
        self, service_id: UUID, company_id: UUID
    ) -> bool: ...

    @abstractmethod
    async def product_belongs_to_company(
        self, product_id: UUID, company_id: UUID
    ) -> bool: ...
