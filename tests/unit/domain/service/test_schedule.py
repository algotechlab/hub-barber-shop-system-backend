from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
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
from src.domain.service.schedule import ScheduleService
from src.infrastructure.database.models.commom.payment_method import PaymentMethod
from src.infrastructure.database.models.commom.payment_status import PaymentStatus

pytestmark = pytest.mark.unit


def _out(company_id):
    return ScheduleOutDTO(
        id=uuid4(),
        user_id=uuid4(),
        service_id=[uuid4()],
        product_id=uuid4(),
        employee_id=uuid4(),
        company_id=company_id,
        time_register='2026-02-14T20:06:18',
        time_start=None,
        time_end=None,
        status=True,
        is_canceled=False,
        created_at='2026-02-14T20:06:18',
        updated_at='2026-02-14T20:06:18',
        is_deleted=False,
    )


@pytest.mark.asyncio
async def test_schedule_service_create_delegates_to_repository():
    repo = AsyncMock()
    service = ScheduleService(repo)
    company_id = uuid4()
    dto = ScheduleCreateDTO(
        user_id=uuid4(),
        service_id=[uuid4()],
        product_id=uuid4(),
        employee_id=uuid4(),
        company_id=company_id,
        time_register='2026-02-14T20:06:18',
        time_start=None,
        time_end=None,
        status=True,
        is_canceled=False,
    )
    expected = _out(company_id)
    repo.create_schedule.return_value = expected

    result = await service.create_schedule(dto)

    repo.create_schedule.assert_awaited_once_with(dto)
    assert result == expected


@pytest.mark.asyncio
async def test_schedule_service_list_delegates_to_repository():
    repo = AsyncMock()
    service = ScheduleService(repo)
    company_id = uuid4()
    pagination = PaginationParamsDTO()
    repo.list_schedules.return_value = []

    result = await service.list_schedules(pagination, company_id)

    repo.list_schedules.assert_awaited_once_with(pagination, company_id, None, None)
    assert result == []


@pytest.mark.asyncio
async def test_schedule_service_get_schedule_by_user_id_delegates_to_repository():
    repo = AsyncMock()
    service = ScheduleService(repo)
    pagination = PaginationParamsDTO()
    company_id = uuid4()
    user_id = uuid4()
    repo.get_schedule_by_user_id.return_value = []

    result = await service.get_schedule_by_user_id(pagination, company_id, user_id)

    repo.get_schedule_by_user_id.assert_awaited_once_with(
        pagination, company_id, user_id
    )
    assert result == []


@pytest.mark.asyncio
async def test_schedule_service_list_history_delegates_to_repository():
    repo = AsyncMock()
    service = ScheduleService(repo)
    pagination = PaginationParamsDTO()
    company_id = uuid4()
    repo.list_schedule_history.return_value = []

    result = await service.list_schedule_history(
        pagination, company_id, True, True, None, None
    )

    repo.list_schedule_history.assert_awaited_once_with(
        pagination, company_id, True, True, None, None
    )
    assert result == []


@pytest.mark.asyncio
async def test_schedule_service_get_slots_delegates_to_repository():
    repo = AsyncMock()
    service = ScheduleService(repo)
    slots = SlotsInDTO(
        company_id=uuid4(),
        employee_id=uuid4(),
        work_start=datetime(2026, 2, 14, 9, 0, 0),
        work_end=datetime(2026, 2, 14, 10, 0, 0),
        slot_minutes=30,
        target_date=None,
    )
    expected = [
        SlotOutDTO(
            id=uuid4(),
            time_start=datetime(2026, 2, 14, 9, 0, 0),
            time_end=datetime(2026, 2, 14, 9, 30, 0),
            is_available=True,
            is_blocked=False,
        )
    ]
    repo.get_slots.return_value = expected

    result = await service.get_slots(slots)

    repo.get_slots.assert_awaited_once_with(slots)
    assert result == expected


@pytest.mark.asyncio
async def test_schedule_service_get_delegates_to_repository():
    repo = AsyncMock()
    service = ScheduleService(repo)
    company_id = uuid4()
    expected = _out(company_id)
    repo.get_schedule.return_value = expected

    result = await service.get_schedule(expected.id, company_id)

    repo.get_schedule.assert_awaited_once_with(expected.id, company_id)
    assert result == expected


@pytest.mark.asyncio
async def test_schedule_service_update_delegates_to_repository():
    repo = AsyncMock()
    service = ScheduleService(repo)
    company_id = uuid4()
    expected = _out(company_id)
    repo.update_schedule.return_value = expected

    result = await service.update_schedule(
        expected.id, ScheduleUpdateDTO(status=False), company_id
    )

    repo.update_schedule.assert_awaited_once()
    assert result == expected


@pytest.mark.asyncio
async def test_schedule_service_delete_delegates_to_repository():
    repo = AsyncMock()
    service = ScheduleService(repo)
    repo.delete_schedule.return_value = True

    result = await service.delete_schedule(uuid4(), uuid4())

    repo.delete_schedule.assert_awaited_once()
    assert result is True


@pytest.mark.asyncio
async def test_schedule_service_block_delegates_to_repository():
    repo = AsyncMock()
    service = ScheduleService(repo)
    repo.block_schedule.return_value = True
    employee_id = uuid4()
    company_id = uuid4()

    result = await service.block_schedule(employee_id, company_id)

    repo.block_schedule.assert_awaited_once_with(employee_id, company_id)
    assert result is True


@pytest.mark.asyncio
async def test_schedule_service_close_delegates_to_repository():
    repo = AsyncMock()
    service = ScheduleService(repo)
    close_dto = CloseScheduleDTO(
        schedule_id=uuid4(),
        company_id=uuid4(),
        created_by=uuid4(),
        amount_service=10,
        amount_product=None,
        amount_discount=None,
        amount_total=10,
        payment_method=PaymentMethod.credit_card,
        payment_status=PaymentStatus.paid,
        paid_at=datetime(2026, 2, 14, 10, 0, 0),
    )
    expected = ScheduleFinanceOutDTO(
        id=uuid4(),
        schedule_id=close_dto.schedule_id,
        service_id=[uuid4()],
        company_id=close_dto.company_id,
        created_by=close_dto.created_by,
        amount_service=10,
        amount_product=None,
        amount_discount=None,
        amount_total=10,
        payment_method=PaymentMethod.credit_card,
        payment_status=PaymentStatus.paid,
        paid_at=close_dto.paid_at,
        created_at=datetime(2026, 2, 14, 10, 0, 0),
        updated_at=datetime(2026, 2, 14, 10, 0, 0),
        is_deleted=False,
    )
    repo.close_schedule.return_value = expected

    result = await service.close_schedule(close_dto)

    repo.close_schedule.assert_awaited_once_with(close_dto)
    assert result == expected


@pytest.mark.asyncio
async def test_schedule_service_sum_sale_delegates_to_repository():
    repo = AsyncMock()
    service = ScheduleService(repo)
    s1, s2 = uuid4(), uuid4()
    company_id = uuid4()
    repo.sum_sale_for_service_ids.return_value = Decimal('15.50')

    result = await service.sum_sale_for_service_ids([s1, s2], company_id)

    repo.sum_sale_for_service_ids.assert_awaited_once_with([s1, s2], company_id)
    assert result == Decimal('15.50')
