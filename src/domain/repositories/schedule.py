from abc import ABC, abstractmethod
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


class ScheduleRepository(ABC):
    @abstractmethod
    async def create_schedule(self, schedule: ScheduleCreateDTO) -> ScheduleOutDTO: ...

    @abstractmethod
    async def list_schedules(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        employee_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
    ) -> List[ScheduleOutDTO]: ...

    @abstractmethod
    async def get_schedule_by_user_id(
        self, pagination: PaginationParamsDTO, company_id: UUID, user_id: UUID
    ) -> List[ScheduleOutDTO]: ...

    @abstractmethod
    async def list_schedule_history(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        include_canceled: bool = True,
        include_finished: bool = True,
        employee_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
    ) -> List[ScheduleOutDTO]: ...

    @abstractmethod
    async def get_slots(self, slots: SlotsInDTO) -> List[SlotOutDTO]: ...

    @abstractmethod
    async def get_schedule(
        self, id: UUID, company_id: UUID
    ) -> Optional[ScheduleOutDTO]: ...

    @abstractmethod
    async def update_schedule(
        self, id: UUID, schedule: ScheduleUpdateDTO, company_id: UUID
    ) -> Optional[ScheduleOutDTO]: ...

    @abstractmethod
    async def block_schedule(self, employee_id: UUID, company_id: UUID) -> None: ...

    @abstractmethod
    async def delete_schedule(self, id: UUID, company_id: UUID) -> Optional[bool]: ...

    @abstractmethod
    async def sum_sale_for_service_ids(
        self, service_ids: List[UUID], company_id: UUID
    ) -> Optional[Decimal]: ...

    @abstractmethod
    async def close_schedule(
        self, close_schedule: CloseScheduleDTO
    ) -> Optional[ScheduleFinanceOutDTO]: ...
