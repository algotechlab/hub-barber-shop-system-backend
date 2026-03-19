from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.schedule import (
    CloseScheduleDTO,
    ScheduleCreateDTO,
    ScheduleFinanceOutDTO,
    ScheduleOutDTO,
    ScheduleUpdateDTO,
    SlotOutDTO,
    SlotsInDTO,
)
from src.domain.repositories.schedule import ScheduleRepository


class ScheduleService:
    def __init__(self, schedule_repository: ScheduleRepository):
        self.schedule_repository = schedule_repository

    async def create_schedule(self, schedule: ScheduleCreateDTO) -> ScheduleOutDTO:
        return await self.schedule_repository.create_schedule(schedule)

    async def list_schedules(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        employee_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
    ) -> List[ScheduleOutDTO]:
        return await self.schedule_repository.list_schedules(
            pagination, company_id, employee_id, user_id
        )

    async def get_schedule_by_user_id(
        self, pagination: PaginationParamsDTO, company_id: UUID, user_id: UUID
    ) -> List[ScheduleOutDTO]:
        return await self.schedule_repository.get_schedule_by_user_id(
            pagination, company_id, user_id
        )

    async def get_slots(self, slots: SlotsInDTO) -> List[SlotOutDTO]:
        return await self.schedule_repository.get_slots(slots)

    async def get_schedule(
        self, id: UUID, company_id: UUID
    ) -> Optional[ScheduleOutDTO]:
        return await self.schedule_repository.get_schedule(id, company_id)

    async def update_schedule(
        self, id: UUID, schedule: ScheduleUpdateDTO, company_id: UUID
    ) -> Optional[ScheduleOutDTO]:
        return await self.schedule_repository.update_schedule(id, schedule, company_id)

    async def block_schedule(self, employee_id: UUID, company_id: UUID) -> None:
        return await self.schedule_repository.block_schedule(employee_id, company_id)

    async def delete_schedule(self, id: UUID, company_id: UUID) -> Optional[bool]:
        return await self.schedule_repository.delete_schedule(id, company_id)

    async def sum_sale_for_service_ids(
        self, service_ids: List[UUID], company_id: UUID
    ) -> Optional[Decimal]:
        return await self.schedule_repository.sum_sale_for_service_ids(
            service_ids, company_id
        )

    async def close_schedule(
        self, close_schedule: CloseScheduleDTO
    ) -> Optional[ScheduleFinanceOutDTO]:
        return await self.schedule_repository.close_schedule(close_schedule)
