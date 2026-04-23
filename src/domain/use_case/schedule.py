from decimal import Decimal
from typing import List
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
from src.domain.exceptions.schedule import (
    ScheduleAlreadyClosedException,
    ScheduleCanceledException,
    ScheduleCloseAmountMismatchException,
    ScheduleCloseServicesException,
    ScheduleNotFoundException,
)
from src.domain.service.schedule import ScheduleService


def _quantize_money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(Decimal('0.01'))


class ScheduleUseCase:
    def __init__(self, schedule_service: ScheduleService):
        self.schedule_service = schedule_service

    async def create_schedule(self, schedule: ScheduleCreateDTO) -> ScheduleOutDTO:
        return await self.schedule_service.create_schedule(schedule)

    async def list_schedules(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        employee_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> List[ScheduleOutDTO]:
        return await self.schedule_service.list_schedules(
            pagination, company_id, employee_id, user_id
        )

    async def get_schedule_by_user_id(
        self, pagination: PaginationParamsDTO, company_id: UUID, user_id: UUID
    ) -> List[ScheduleOutDTO]:
        return await self.schedule_service.get_schedule_by_user_id(
            pagination, company_id, user_id
        )

    async def list_schedule_history(
        self,
        pagination: PaginationParamsDTO,
        company_id: UUID,
        include_canceled: bool = True,
        include_finished: bool = True,
        employee_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> List[ScheduleOutDTO]:
        return await self.schedule_service.list_schedule_history(
            pagination,
            company_id,
            include_canceled,
            include_finished,
            employee_id,
            user_id,
        )

    async def get_slots(self, slots: SlotsInDTO) -> List[SlotOutDTO]:
        return await self.schedule_service.get_slots(slots)

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

    async def block_schedule(self, employee_id: UUID, company_id: UUID) -> None:
        return await self.schedule_service.block_schedule(employee_id, company_id)

    async def delete_schedule(self, id: UUID, company_id: UUID) -> bool:
        deleted = await self.schedule_service.delete_schedule(id, company_id)
        if deleted is None:
            raise ScheduleNotFoundException('Agendamento não encontrado')
        return deleted

    async def close_schedule(
        self, close_schedule: CloseScheduleDTO
    ) -> ScheduleFinanceOutDTO:
        schedule = await self.schedule_service.get_schedule(
            close_schedule.schedule_id, close_schedule.company_id
        )
        if schedule is None:
            raise ScheduleNotFoundException('Agendamento não encontrado')
        if schedule.is_canceled:
            raise ScheduleCanceledException(
                'Não é possível fechar um agendamento cancelado'
            )

        expected_total = await self.schedule_service.sum_sale_for_service_ids(
            schedule.service_id, close_schedule.company_id
        )
        if expected_total is None:
            raise ScheduleCloseServicesException(
                'Um ou mais serviços do agendamento são inválidos ou inativos.'
            )
        if _quantize_money(close_schedule.amount_service) != _quantize_money(
            expected_total
        ):
            raise ScheduleCloseAmountMismatchException(
                f'amount_service deve ser {_quantize_money(expected_total)} '
                '(soma dos preços dos serviços vinculados ao agendamento).'
            )

        schedule_finance = await self.schedule_service.close_schedule(close_schedule)
        if schedule_finance is None:
            raise ScheduleAlreadyClosedException('Agendamento já foi fechado')
        return schedule_finance
