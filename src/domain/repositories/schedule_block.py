from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.dtos.schedule_block import (
    ScheduleBlockCreateDTO,
    ScheduleBlockOutDTO,
    ScheduleBlockUpdateDTO,
)


class ScheduleBlockRepository(ABC):
    @abstractmethod
    async def create_schedule_block(
        self, schedule_block: ScheduleBlockCreateDTO
    ) -> ScheduleBlockOutDTO: ...

    @abstractmethod
    async def get_schedule_block(self, id: UUID) -> Optional[ScheduleBlockOutDTO]: ...

    @abstractmethod
    async def update_schedule_block(
        self, id: UUID, schedule_block: ScheduleBlockUpdateDTO
    ) -> Optional[ScheduleBlockOutDTO]: ...

    @abstractmethod
    async def delete_schedule_block(self, id: UUID) -> bool: ...
