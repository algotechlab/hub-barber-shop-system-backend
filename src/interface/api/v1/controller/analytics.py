from uuid import UUID

from src.domain.dtos.analytics import DashboardFilterDTO
from src.domain.use_case.analytics import AnalyticsUseCase
from src.interface.api.v1.schema.analytics import (
    DashboardFilterInSchema,
    DashboardMetricsOutSchema,
)


class AnalyticsController:
    def __init__(self, analytics_use_case: AnalyticsUseCase):
        self.analytics_use_case = analytics_use_case

    async def get_dashboard_metrics(
        self, dashboard_filter: DashboardFilterInSchema, company_id: UUID
    ) -> DashboardMetricsOutSchema:
        dashboard_filter_dto = DashboardFilterDTO(
            company_id=company_id, **dashboard_filter.model_dump()
        )
        metrics = await self.analytics_use_case.get_dashboard_metrics(
            dashboard_filter_dto
        )
        return DashboardMetricsOutSchema(**metrics.model_dump())
