from abc import ABC, abstractmethod

from src.domain.dtos.analytics import DashboardFilterDTO, DashboardMetricsDTO


class AnalyticsRepository(ABC):
    @abstractmethod
    async def get_dashboard_metrics(
        self, dashboard_filter: DashboardFilterDTO
    ) -> DashboardMetricsDTO: ...
