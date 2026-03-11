from datetime import datetime
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
from src.domain.exceptions.schedule import (
    ScheduleAlreadyClosedException,
    ScheduleCanceledException,
    ScheduleNotFoundException,
)
from src.domain.use_case.schedule import ScheduleUseCase
from src.infrastructure.database.models.commom.payment_method import PaymentMethod
from src.infrastructure.database.models.commom.payment_status import PaymentStatus

pytestmark = pytest.mark.unit


def _out(company_id):
    return ScheduleOutDTO(
        id=uuid4(),
        user_id=uuid4(),
        service_id=uuid4(),
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
async def test_create_schedule_delegates_to_service_layer():
    service = AsyncMock()
    use_case = ScheduleUseCase(service)
    company_id = uuid4()
    dto = ScheduleCreateDTO(
        user_id=uuid4(),
        service_id=uuid4(),
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
    service.create_schedule.return_value = expected

    result = await use_case.create_schedule(dto)

    service.create_schedule.assert_awaited_once_with(dto)
    assert result == expected


@pytest.mark.asyncio
async def test_list_schedules_delegates_to_service_layer():
    service = AsyncMock()
    service.list_schedules.return_value = []
    use_case = ScheduleUseCase(service)
    pagination = PaginationParamsDTO()
    company_id = uuid4()

    result = await use_case.list_schedules(pagination, company_id)

    service.list_schedules.assert_awaited_once_with(pagination, company_id, None, None)
    assert result == []


@pytest.mark.asyncio
async def test_get_schedule_by_user_id_delegates_to_service_layer():
    service = AsyncMock()
    service.get_schedule_by_user_id.return_value = []
    use_case = ScheduleUseCase(service)
    pagination = PaginationParamsDTO()
    company_id = uuid4()
    user_id = uuid4()

    result = await use_case.get_schedule_by_user_id(pagination, company_id, user_id)

    service.get_schedule_by_user_id.assert_awaited_once_with(
        pagination, company_id, user_id
    )
    assert result == []


@pytest.mark.asyncio
async def test_get_slots_delegates_to_service_layer():
    service = AsyncMock()
    use_case = ScheduleUseCase(service)
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
    service.get_slots.return_value = expected

    result = await use_case.get_slots(slots)

    service.get_slots.assert_awaited_once_with(slots)
    assert result == expected


@pytest.mark.asyncio
async def test_get_schedule_raises_when_not_found():
    service = AsyncMock()
    service.get_schedule.return_value = None
    use_case = ScheduleUseCase(service)

    with pytest.raises(ScheduleNotFoundException):
        await use_case.get_schedule(uuid4(), uuid4())


@pytest.mark.asyncio
async def test_get_schedule_returns_when_found():
    service = AsyncMock()
    company_id = uuid4()
    expected = _out(company_id)
    service.get_schedule.return_value = expected
    use_case = ScheduleUseCase(service)

    result = await use_case.get_schedule(expected.id, company_id)

    assert result == expected


@pytest.mark.asyncio
async def test_update_schedule_raises_when_not_found():
    service = AsyncMock()
    service.update_schedule.return_value = None
    use_case = ScheduleUseCase(service)

    with pytest.raises(ScheduleNotFoundException):
        await use_case.update_schedule(
            uuid4(), ScheduleUpdateDTO(status=False), uuid4()
        )


@pytest.mark.asyncio
async def test_update_schedule_returns_when_found():
    service = AsyncMock()
    company_id = uuid4()
    expected = _out(company_id)
    service.update_schedule.return_value = expected
    use_case = ScheduleUseCase(service)

    result = await use_case.update_schedule(
        expected.id, ScheduleUpdateDTO(status=False), company_id
    )

    assert result == expected


@pytest.mark.asyncio
async def test_delete_schedule_raises_when_not_found():
    service = AsyncMock()
    service.delete_schedule.return_value = None
    use_case = ScheduleUseCase(service)

    with pytest.raises(ScheduleNotFoundException):
        await use_case.delete_schedule(uuid4(), uuid4())


@pytest.mark.asyncio
async def test_delete_schedule_returns_true_when_deleted():
    service = AsyncMock()
    service.delete_schedule.return_value = True
    use_case = ScheduleUseCase(service)

    result = await use_case.delete_schedule(uuid4(), uuid4())

    assert result is True


@pytest.mark.asyncio
async def test_block_schedule_delegates_to_service_layer():
    service = AsyncMock()
    service.block_schedule.return_value = True
    use_case = ScheduleUseCase(service)
    employee_id = uuid4()
    company_id = uuid4()

    result = await use_case.block_schedule(employee_id, company_id)

    service.block_schedule.assert_awaited_once_with(employee_id, company_id)
    assert result is True


@pytest.mark.asyncio
async def test_close_schedule_raises_when_not_found():
    service = AsyncMock()
    service.get_schedule.return_value = None
    use_case = ScheduleUseCase(service)
    close_dto = CloseScheduleDTO(
        schedule_id=uuid4(),
        company_id=uuid4(),
        created_by=uuid4(),
        amount_service=10,
        amount_product=None,
        amount_discount=None,
        amount_total=10,
        payment_method=PaymentMethod.pix,
        payment_status=PaymentStatus.paid,
        paid_at=datetime(2026, 2, 14, 10, 0, 0),
    )

    with pytest.raises(ScheduleNotFoundException):
        await use_case.close_schedule(close_dto)


@pytest.mark.asyncio
async def test_close_schedule_raises_when_canceled():
    service = AsyncMock()
    schedule = _out(uuid4())
    schedule.is_canceled = True
    service.get_schedule.return_value = schedule
    use_case = ScheduleUseCase(service)
    close_dto = CloseScheduleDTO(
        schedule_id=schedule.id,
        company_id=schedule.company_id,
        created_by=uuid4(),
        amount_service=10,
        amount_product=None,
        amount_discount=None,
        amount_total=10,
        payment_method=PaymentMethod.pix,
        payment_status=PaymentStatus.paid,
        paid_at=datetime(2026, 2, 14, 10, 0, 0),
    )

    with pytest.raises(ScheduleCanceledException):
        await use_case.close_schedule(close_dto)


@pytest.mark.asyncio
async def test_close_schedule_raises_when_already_closed():
    service = AsyncMock()
    schedule = _out(uuid4())
    schedule.is_canceled = False
    service.get_schedule.return_value = schedule
    service.close_schedule.return_value = None
    use_case = ScheduleUseCase(service)
    close_dto = CloseScheduleDTO(
        schedule_id=schedule.id,
        company_id=schedule.company_id,
        created_by=uuid4(),
        amount_service=10,
        amount_product=None,
        amount_discount=None,
        amount_total=10,
        payment_method=PaymentMethod.pix,
        payment_status=PaymentStatus.paid,
        paid_at=datetime(2026, 2, 14, 10, 0, 0),
    )

    with pytest.raises(ScheduleAlreadyClosedException):
        await use_case.close_schedule(close_dto)


@pytest.mark.asyncio
async def test_close_schedule_returns_finance_when_success():
    service = AsyncMock()
    schedule = _out(uuid4())
    schedule.is_canceled = False
    service.get_schedule.return_value = schedule
    finance = ScheduleFinanceOutDTO(
        id=uuid4(),
        schedule_id=schedule.id,
        company_id=schedule.company_id,
        created_by=uuid4(),
        amount_service=10,
        amount_product=None,
        amount_discount=None,
        amount_total=10,
        payment_method=PaymentMethod.pix,
        payment_status=PaymentStatus.paid,
        paid_at=datetime(2026, 2, 14, 10, 0, 0),
        created_at=datetime(2026, 2, 14, 10, 0, 0),
        updated_at=datetime(2026, 2, 14, 10, 0, 0),
        is_deleted=False,
    )
    service.close_schedule.return_value = finance
    use_case = ScheduleUseCase(service)
    close_dto = CloseScheduleDTO(
        schedule_id=schedule.id,
        company_id=schedule.company_id,
        created_by=finance.created_by,
        amount_service=10,
        amount_product=None,
        amount_discount=None,
        amount_total=10,
        payment_method=PaymentMethod.pix,
        payment_status=PaymentStatus.paid,
        paid_at=datetime(2026, 2, 14, 10, 0, 0),
    )

    result = await use_case.close_schedule(close_dto)

    assert result == finance
