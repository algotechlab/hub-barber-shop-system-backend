from datetime import datetime, timezone
from typing import List
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.user_subscription import (
    UserSubscriptionCreateDTO,
    UserSubscriptionOutDTO,
    UserSubscriptionWithPlanOutDTO,
)
from src.domain.exceptions.subscription import (
    SubscriptionPlanNotFoundException,
    UserSubscriptionActiveExistsException,
)
from src.domain.service.subscription_plan import SubscriptionPlanService
from src.domain.service.user_subscription import UserSubscriptionService


class UserSubscriptionUseCase:
    def __init__(
        self,
        user_subscription_service: UserSubscriptionService,
        subscription_plan_service: SubscriptionPlanService,
    ):
        self._us = user_subscription_service
        self._plan = subscription_plan_service

    async def create_for_user(
        self,
        *,
        user_id: UUID,
        company_id: UUID,
        subscription_plan_id: UUID,
        external_subscription_id: str | None = None,
    ) -> UserSubscriptionOutDTO:
        plan = await self._plan.get_plan(
            subscription_plan_id, company_id, active_only=True
        )
        if plan is None:
            raise SubscriptionPlanNotFoundException(
                'Plano de assinatura não encontrado ou inativo'
            )

        if await self._us.has_active_for_plan(
            user_id, subscription_plan_id, company_id
        ):
            raise UserSubscriptionActiveExistsException(
                'Você já possui assinatura ativa deste plano'
            )

        dto = UserSubscriptionCreateDTO(
            user_id=user_id,
            company_id=company_id,
            subscription_plan_id=subscription_plan_id,
            started_at=datetime.now(timezone.utc),
            external_subscription_id=external_subscription_id,
        )
        return await self._us.create(dto)

    async def list_mine(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        user_id: UUID,
    ) -> List[UserSubscriptionWithPlanOutDTO]:
        return await self._us.list_by_user(pagination, company_id, user_id)
