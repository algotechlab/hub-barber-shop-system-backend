from typing import Annotated

from fastapi import Depends

from src.domain.service.subscription_plan import SubscriptionPlanService
from src.domain.service.user_subscription import UserSubscriptionService
from src.domain.use_case.user_subscription import UserSubscriptionUseCase
from src.infrastructure.repositories.subscription_plan_postgres import (
    SubscriptionPlanRepositoryPostgres,
)
from src.infrastructure.repositories.user_subscription_postgres import (
    UserSubscriptionRepositoryPostgres,
)
from src.interface.api.v1.controller.user_subscription import UserSubscriptionController
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep


async def get_user_subscription_controller(
    session: VerifiedSessionDep,
) -> UserSubscriptionController:
    us_repo = UserSubscriptionRepositoryPostgres(session)
    plan_repo = SubscriptionPlanRepositoryPostgres(session)
    us_service = UserSubscriptionService(us_repo)
    plan_service = SubscriptionPlanService(plan_repo)
    use_case = UserSubscriptionUseCase(us_service, plan_service)
    return UserSubscriptionController(use_case)


UserSubscriptionControllerDep = Annotated[
    UserSubscriptionController, Depends(get_user_subscription_controller)
]
