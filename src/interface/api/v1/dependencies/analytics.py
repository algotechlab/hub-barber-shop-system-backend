from typing import Annotated

from fastapi import Depends

from src.domain.service.analytics import AnalyticsService
from src.domain.use_case.analytics import AnalyticsUseCase
from src.infrastructure.repositories.analytics_postgres import (
    AnalyticsRepositoryPostgres,
)
from src.interface.api.v1.controller.analytics import AnalyticsController
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep


async def get_analytics_controller(session: VerifiedSessionDep) -> AnalyticsController:
    analytics_repository = AnalyticsRepositoryPostgres(session)
    analytics_service = AnalyticsService(analytics_repository)
    analytics_use_case = AnalyticsUseCase(analytics_service)
    return AnalyticsController(analytics_use_case)


AnalyticsRepositoryDep = Annotated[
    AnalyticsController, Depends(get_analytics_controller)
]
