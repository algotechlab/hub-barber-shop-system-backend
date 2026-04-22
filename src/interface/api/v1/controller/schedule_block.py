from typing import List
from uuid import UUID

from src.domain.dtos.schedule_block import (
    ScheduleBlockCreateDTO,
    ScheduleBlockUpdateDTO,
)
from src.domain.use_case.schedule_block import ScheduleBlockUseCase
from src.interface.api.v1.schema.schedule_block import (
    CreateScheduleBlockSchema,
    ScheduleBlockOutListSchema,
    ScheduleBlockOutSchema,
    UpdateScheduleBlockSchema,
)


class ScheduleBlockController:
    def __init__(self, schedule_block_use_case: ScheduleBlockUseCase):
        self.schedule_block_use_case = schedule_block_use_case

    async def create_schedule_block(
        self, schedule_block: CreateScheduleBlockSchema, company_id: UUID
    ) -> ScheduleBlockOutSchema:
        schedule_block_dto = ScheduleBlockCreateDTO(
            **schedule_block.model_dump(), company_id=company_id
        )
        created_schedule_block = (
            await self.schedule_block_use_case.create_schedule_block(schedule_block_dto)
        )
        return ScheduleBlockOutSchema(**created_schedule_block.model_dump())

    async def list_schedule_blocks(
        self, company_id: UUID
    ) -> List[ScheduleBlockOutListSchema]:
        schedule_blocks = await self.schedule_block_use_case.list_schedule_blocks(
            company_id
        )
        return [
            ScheduleBlockOutListSchema(**schedule_block.model_dump())
            for schedule_block in schedule_blocks
        ]

    async def get_schedule_block(self, id: UUID) -> ScheduleBlockOutSchema:
        schedule_block = await self.schedule_block_use_case.get_schedule_block(id)
        return ScheduleBlockOutSchema(**schedule_block.model_dump())

    async def update_schedule_block(
        self, id: UUID, schedule_block: UpdateScheduleBlockSchema
    ) -> ScheduleBlockOutSchema:
        schedule_block_dto = ScheduleBlockUpdateDTO(**schedule_block.model_dump())
        updated = await self.schedule_block_use_case.update_schedule_block(
            id, schedule_block_dto
        )
        return ScheduleBlockOutSchema(**updated.model_dump())

    async def delete_schedule_block(self, id: UUID) -> bool:
        return await self.schedule_block_use_case.delete_schedule_block(id)
