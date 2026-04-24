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

    async def _validate_services(
        self, company_id: UUID, service_ids: List[UUID]
    ) -> None:
        for sid in service_ids:
            if not await self._service.service_belongs_to_company(sid, company_id):
                raise SubscriptionPlanServiceMismatchException(
                    'Serviço inexistente ou de outra empresa'
                )

    async def _validate_products(
        self, company_id: UUID, product_ids: List[UUID]
    ) -> None:
        for pid in product_ids:
            if not await self._service.product_belongs_to_company(pid, company_id):
                raise SubscriptionPlanServiceMismatchException(
                    'Produto inexistente ou de outra empresa'
                )

    async def create_plan(
        self, data: SubscriptionPlanCreateDTO
    ) -> SubscriptionPlanOutDTO:
        await self._validate_services(data.company_id, data.service_ids)
        if data.product_lines:
            await self._validate_products(
                data.company_id, [p.product_id for p in data.product_lines]
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
        if data.service_ids is not None:
            await self._validate_services(company_id, data.service_ids)
        if data.product_lines is not None and data.product_lines:
            await self._validate_products(
                company_id, [p.product_id for p in data.product_lines]
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
