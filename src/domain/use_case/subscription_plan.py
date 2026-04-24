from typing import List
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.subscription_plan import (
    SubscriptionPlanCreateDTO,
    SubscriptionPlanOutDTO,
    SubscriptionPlanUpdateDTO,
)
from src.domain.exceptions.subscription import (
    SubscriptionPlanNotFoundException,
    SubscriptionPlanServiceMismatchException,
)
from src.domain.service.subscription_plan import SubscriptionPlanService


class SubscriptionPlanUseCase:
    def __init__(self, service: SubscriptionPlanService):
        self._service = service

    async def create_plan(
        self, data: SubscriptionPlanCreateDTO
    ) -> SubscriptionPlanOutDTO:
        if not await self._service.service_belongs_to_company(
            data.service_id, data.company_id
        ):
            raise SubscriptionPlanServiceMismatchException(
                'Serviço inexistente ou de outra empresa'
            )
        return await self._service.create_plan(data)

    async def get_plan(
        self,
        id: UUID,
        company_id: UUID,
        *,
        active_only: bool = False,
    ) -> SubscriptionPlanOutDTO:
        plan = await self._service.get_plan(id, company_id, active_only=active_only)
        if plan is None:
            raise SubscriptionPlanNotFoundException(
                'Plano de assinatura não encontrado'
            )
        return plan

    async def list_plans(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        *,
        active_only: bool = False,
    ) -> List[SubscriptionPlanOutDTO]:
        return await self._service.list_plans(
            pagination, company_id, active_only=active_only
        )

    async def update_plan(
        self, id: UUID, data: SubscriptionPlanUpdateDTO, company_id: UUID
    ) -> SubscriptionPlanOutDTO:
        if data.service_id is not None:
            if not await self._service.service_belongs_to_company(
                data.service_id, company_id
            ):
                raise SubscriptionPlanServiceMismatchException(
                    'Serviço inexistente ou de outra empresa'
                )
        updated = await self._service.update_plan(id, data, company_id)
        if updated is None:
            raise SubscriptionPlanNotFoundException(
                'Plano de assinatura não encontrado'
            )
        return updated

    async def delete_plan(self, id: UUID, company_id: UUID) -> bool:
        ok = await self._service.delete_plan(id, company_id)
        if not ok:
            raise SubscriptionPlanNotFoundException(
                'Plano de assinatura não encontrado'
            )
        return True
