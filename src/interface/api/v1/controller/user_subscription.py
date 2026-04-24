from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.use_case.user_subscription import UserSubscriptionUseCase
from src.interface.api.v1.schema.user_subscription import (
    ActivateUserSubscriptionAfterPaymentSchema,
    CreateUserSubscriptionSchema,
    UserSubscriptionOutSchema,
    UserSubscriptionWithPlanAndClientOutSchema,
    UserSubscriptionWithPlanOutSchema,
)


class UserSubscriptionController:
    def __init__(self, use_case: UserSubscriptionUseCase):
        self._use_case = use_case

    async def create(
        self,
        body: CreateUserSubscriptionSchema,
        company_id: UUID,
        user_id: UUID,
    ) -> UserSubscriptionOutSchema:
        out = await self._use_case.create_for_user(
            user_id=user_id,
            company_id=company_id,
            subscription_plan_id=body.subscription_plan_id,
            external_subscription_id=body.external_subscription_id,
        )
        return UserSubscriptionOutSchema(**out.model_dump())

    async def list_mine(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        user_id: UUID,
    ) -> list[UserSubscriptionWithPlanOutSchema]:
        rows = await self._use_case.list_mine(pagination, company_id, user_id)
        return [UserSubscriptionWithPlanOutSchema(**r.model_dump()) for r in rows]

    async def list_pending(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        client_name: str | None = None,
    ) -> list[UserSubscriptionWithPlanAndClientOutSchema]:
        rows = await self._use_case.list_pending_for_company(
            pagination, company_id, client_name=client_name
        )
        return [
            UserSubscriptionWithPlanAndClientOutSchema(**r.model_dump()) for r in rows
        ]

    async def activate_after_payment(
        self,
        subscription_id: UUID,
        company_id: UUID,
        body: ActivateUserSubscriptionAfterPaymentSchema,
    ) -> UserSubscriptionOutSchema:
        out = await self._use_case.activate_after_payment(
            subscription_id=subscription_id,
            company_id=company_id,
            external_subscription_id=body.external_subscription_id,
            payment_method=body.payment_method,
            payment_at=body.payment_at,
        )
        return UserSubscriptionOutSchema(**out.model_dump())
