from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.dtos.marketing import InactiveClientsPayloadDTO


class MarketingInactiveRepository(ABC):
    @abstractmethod
    async def fetch_inactive_clients(
        self,
        company_id: UUID,
        *,
        email: str | None = None,
        min_days: int | None = None,
        max_days: int | None = None,
        lookback_years: int = 2,
        schedules_limit: int = 3000,
    ) -> InactiveClientsPayloadDTO: ...
