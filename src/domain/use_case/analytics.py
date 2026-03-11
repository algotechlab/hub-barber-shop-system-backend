from src.domain.dtos.analytics import DashboardFilterDTO, DashboardMetricsDTO
from src.domain.service.analytics import AnalyticsService


class AnalyticsUseCase:
    def __init__(self, analytics_service: AnalyticsService):
        self.analytics_service = analytics_service

    async def get_dashboard_metrics(
        self, dashboard_filter: DashboardFilterDTO
    ) -> DashboardMetricsDTO:
        return await self.analytics_service.get_dashboard_metrics(dashboard_filter)
