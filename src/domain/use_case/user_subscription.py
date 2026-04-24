from datetime import datetime, timezone
from typing import List
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.user_subscription import (
    UserSubscriptionCreateDTO,
    UserSubscriptionOutDTO,
    UserSubscriptionWithPlanAndClientOutDTO,
    UserSubscriptionWithPlanOutDTO,
)
from src.domain.exceptions.subscription import (
    SubscriptionPlanNotFoundException,
    UserSubscriptionActiveExistsException,
    UserSubscriptionInvalidStateException,
    UserSubscriptionNotFoundException,
    UserSubscriptionPendingExistsException,
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

        if await self._us.has_pending_for_plan(
            user_id, subscription_plan_id, company_id
        ):
            raise UserSubscriptionPendingExistsException(
                'Já existe solicitação pendente para este plano'
            )

        dto = UserSubscriptionCreateDTO(
            user_id=user_id,
            company_id=company_id,
            subscription_plan_id=subscription_plan_id,
            status='PENDING_PAYMENT',
            started_at=datetime.now(timezone.utc),
            external_subscription_id=external_subscription_id,
        )
        return await self._us.create(dto)

    async def list_pending_for_company(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        client_name: str | None = None,
    ) -> List[UserSubscriptionWithPlanAndClientOutDTO]:
        return await self._us.list_pending_by_company(
            pagination, company_id, client_name=client_name
        )

    async def activate_after_payment(
        self,
        *,
        subscription_id: UUID,
        company_id: UUID,
        external_subscription_id: str | None = None,
        payment_method: str,
        payment_at: datetime | None = None,
    ) -> UserSubscriptionOutDTO:
        updated = await self._us.activate_pending(
            subscription_id,
            company_id,
            external_subscription_id=external_subscription_id,
            payment_method=payment_method,
            payment_at=payment_at,
        )
        if updated is not None:
            return updated
        existing = await self._us.get_by_id(subscription_id, company_id)
        if existing is None:
            raise UserSubscriptionNotFoundException('Assinatura não encontrada')
        raise UserSubscriptionInvalidStateException(
            'Somente solicitações em PENDING_PAYMENT podem ser ativadas '
            'após o pagamento'
        )

    async def list_mine(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        user_id: UUID,
    ) -> List[UserSubscriptionWithPlanOutDTO]:
        return await self._us.list_by_user(pagination, company_id, user_id)
