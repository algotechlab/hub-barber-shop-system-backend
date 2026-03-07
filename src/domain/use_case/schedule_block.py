from typing import Optional
from uuid import UUID

from src.domain.dtos.schedule_block import (
    ScheduleBlockCreateDTO,
    ScheduleBlockOutDTO,
    ScheduleBlockUpdateDTO,
)
from src.domain.exceptions.schedule_block import ScheduleBlockNotFoundException
from src.domain.service.schedule_block import ScheduleBlockService


class ScheduleBlockUseCase:
    def __init__(self, schedule_block_service: ScheduleBlockService):
        self.schedule_block_service = schedule_block_service

    async def create_schedule_block(
        self, schedule_block: ScheduleBlockCreateDTO
    ) -> ScheduleBlockOutDTO:
        return await self.schedule_block_service.create_schedule_block(schedule_block)

    async def get_schedule_block(self, id: UUID) -> Optional[ScheduleBlockOutDTO]:
        schedule_block = await self.schedule_block_service.get_schedule_block(id)
        if schedule_block is None:
            raise ScheduleBlockNotFoundException('Funcionário não encontrado')
        return schedule_block

    async def update_schedule_block(
        self, id: UUID, schedule_block: ScheduleBlockUpdateDTO
    ) -> Optional[ScheduleBlockOutDTO]:
        return await self.schedule_block_service.update_schedule_block(
            id, schedule_block
        )

    async def delete_schedule_block(self, id: UUID) -> bool:
        deleted = await self.schedule_block_service.delete_schedule_block(id)
        if not deleted:
            raise ScheduleBlockNotFoundException('Funcionário não encontrado')
        return deleted
