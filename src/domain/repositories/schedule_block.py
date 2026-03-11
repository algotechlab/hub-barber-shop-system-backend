from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.dtos.schedule_block import (
    ScheduleBlockCreateDTO,
    ScheduleBlockOutDTO,
    ScheduleBlockOutListDTO,
    ScheduleBlockUpdateDTO,
)


class ScheduleBlockRepository(ABC):
    @abstractmethod
    async def create_schedule_block(
        self, schedule_block: ScheduleBlockCreateDTO
    ) -> ScheduleBlockOutDTO: ...

    @abstractmethod
    async def list_schedule_blocks(
        self, company_id: UUID
    ) -> List[ScheduleBlockOutListDTO]: ...

    @abstractmethod
    async def get_schedule_block(self, id: UUID) -> Optional[ScheduleBlockOutDTO]: ...

    @abstractmethod
    async def update_schedule_block(
        self, id: UUID, schedule_block: ScheduleBlockUpdateDTO
    ) -> Optional[ScheduleBlockOutDTO]: ...

    @abstractmethod
    async def delete_schedule_block(self, id: UUID) -> bool: ...
