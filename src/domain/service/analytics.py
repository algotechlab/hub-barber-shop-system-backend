from src.domain.dtos.analytics import DashboardFilterDTO, DashboardMetricsDTO
from src.domain.repositories.analytics import AnalyticsRepository


class AnalyticsService:
    def __init__(self, analytics_repository: AnalyticsRepository):
        self.analytics_repository = analytics_repository

    async def get_dashboard_metrics(
        self, dashboard_filter: DashboardFilterDTO
    ) -> DashboardMetricsDTO:
        return await self.analytics_repository.get_dashboard_metrics(dashboard_filter)
