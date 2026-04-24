from typing import Annotated

from fastapi import Depends

from src.domain.service.subscription_plan import SubscriptionPlanService
from src.domain.use_case.subscription_plan import SubscriptionPlanUseCase
from src.infrastructure.repositories.subscription_plan_postgres import (
    SubscriptionPlanRepositoryPostgres,
)
from src.interface.api.v1.controller.subscription_plan import SubscriptionPlanController
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep


async def get_subscription_plan_controller(
    session: VerifiedSessionDep,
) -> SubscriptionPlanController:
    repository = SubscriptionPlanRepositoryPostgres(session)
    service = SubscriptionPlanService(repository)
    use_case = SubscriptionPlanUseCase(service)
    return SubscriptionPlanController(use_case)


SubscriptionPlanControllerDep = Annotated[
    SubscriptionPlanController, Depends(get_subscription_plan_controller)
]
