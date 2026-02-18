from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.schedule import (
    ScheduleCreateDTO,
    ScheduleOutDTO,
    ScheduleUpdateDTO,
)


class ScheduleRepository(ABC):
    @abstractmethod
    async def create_schedule(self, schedule: ScheduleCreateDTO) -> ScheduleOutDTO: ...

    @abstractmethod
    async def list_schedules(
        self, pagination: PaginationParamsDTO, company_id: UUID
    ) -> List[ScheduleOutDTO]: ...

    @abstractmethod
    async def get_schedule(
        self, id: UUID, company_id: UUID
    ) -> Optional[ScheduleOutDTO]: ...

    @abstractmethod
    async def update_schedule(
        self, id: UUID, schedule: ScheduleUpdateDTO, company_id: UUID
    ) -> Optional[ScheduleOutDTO]: ...

    @abstractmethod
    async def delete_schedule(self, id: UUID, company_id: UUID) -> Optional[bool]: ...
