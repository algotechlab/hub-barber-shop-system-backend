from typing import Optional
from uuid import UUID

from src.domain.dtos.schedule_block import (
    ScheduleBlockCreateDTO,
    ScheduleBlockOutDTO,
    ScheduleBlockUpdateDTO,
)
from src.domain.repositories.schedule_block import ScheduleBlockRepository


class ScheduleBlockService:
    def __init__(self, schedule_block_repository: ScheduleBlockRepository):
        self.schedule_block_repository = schedule_block_repository

    async def create_schedule_block(
        self, schedule_block: ScheduleBlockCreateDTO
    ) -> ScheduleBlockOutDTO:
        return await self.schedule_block_repository.create_schedule_block(
            schedule_block
        )

    async def get_schedule_block(self, id: UUID) -> Optional[ScheduleBlockOutDTO]:
        return await self.schedule_block_repository.get_schedule_block(id)

    async def update_schedule_block(
        self, id: UUID, schedule_block: ScheduleBlockUpdateDTO
    ) -> Optional[ScheduleBlockOutDTO]:
        return await self.schedule_block_repository.update_schedule_block(
            id, schedule_block
        )

    async def delete_schedule_block(self, id: UUID) -> bool:
        return await self.schedule_block_repository.delete_schedule_block(id)
