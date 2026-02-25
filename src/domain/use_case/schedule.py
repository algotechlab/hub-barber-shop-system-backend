from typing import List
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.schedule import (
    ScheduleCreateDTO,
    ScheduleOutDTO,
    ScheduleUpdateDTO,
)
from src.domain.exceptions.schedule import ScheduleNotFoundException
from src.domain.service.schedule import ScheduleService


class ScheduleUseCase:
    def __init__(self, schedule_service: ScheduleService):
        self.schedule_service = schedule_service

    async def create_schedule(self, schedule: ScheduleCreateDTO) -> ScheduleOutDTO:
        return await self.schedule_service.create_schedule(schedule)

    async def list_schedules(
        self, pagination: PaginationParamsDTO, company_id: UUID
    ) -> List[ScheduleOutDTO]:
        return await self.schedule_service.list_schedules(pagination, company_id)

    async def get_schedule(self, id: UUID, company_id: UUID) -> ScheduleOutDTO:
        schedule = await self.schedule_service.get_schedule(id, company_id)
        if schedule is None:
            raise ScheduleNotFoundException('Agendamento não encontrado')
        return schedule

    async def update_schedule(
        self, id: UUID, schedule: ScheduleUpdateDTO, company_id: UUID
    ) -> ScheduleOutDTO:
        updated_schedule = await self.schedule_service.update_schedule(
            id, schedule, company_id
        )
        if updated_schedule is None:
            raise ScheduleNotFoundException('Agendamento não encontrado')
        return updated_schedule

    async def delete_schedule(self, id: UUID, company_id: UUID) -> bool:
        deleted = await self.schedule_service.delete_schedule(id, company_id)
        if deleted is None:
            raise ScheduleNotFoundException('Agendamento não encontrado')
        return deleted
