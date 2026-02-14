from typing import List
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.schedule import (
    ScheduleCreateDTO,
    ScheduleUpdateDTO,
)
from src.domain.use_case.schedule import ScheduleUseCase
from src.interface.api.v1.schema.schedule import (
    CreateScheduleSchema,
    ScheduleOutSchema,
    UpdateScheduleSchema,
)


class ScheduleController:
    def __init__(self, schedule_use_case: ScheduleUseCase):
        self.schedule_use_case = schedule_use_case

    async def create_schedule(
        self, schedule: CreateScheduleSchema, company_id: UUID
    ) -> ScheduleOutSchema:
        schedule_dto = ScheduleCreateDTO(
            **schedule.model_dump(exclude={'company_id'}), company_id=company_id
        )
        created_schedule = await self.schedule_use_case.create_schedule(schedule_dto)
        return ScheduleOutSchema(**created_schedule.model_dump())

    async def list_schedules(
        self, pagination: PaginationParamsDTO, company_id: UUID
    ) -> List[ScheduleOutSchema]:
        schedules = await self.schedule_use_case.list_schedules(pagination, company_id)
        return [ScheduleOutSchema(**schedule.model_dump()) for schedule in schedules]

    async def get_schedule(self, id: UUID, company_id: UUID) -> ScheduleOutSchema:
        schedule = await self.schedule_use_case.get_schedule(id, company_id)
        return ScheduleOutSchema(**schedule.model_dump())

    async def update_schedule(
        self, id: UUID, schedule: UpdateScheduleSchema, company_id: UUID
    ) -> ScheduleOutSchema:
        schedule_dto = ScheduleUpdateDTO(
            **schedule.model_dump(exclude={'company_id'}), company_id=company_id
        )
        updated_schedule = await self.schedule_use_case.update_schedule(
            id, schedule_dto, company_id
        )
        return ScheduleOutSchema(**updated_schedule.model_dump())

    async def delete_schedule(self, id: UUID, company_id: UUID) -> None:
        await self.schedule_use_case.delete_schedule(id, company_id)
