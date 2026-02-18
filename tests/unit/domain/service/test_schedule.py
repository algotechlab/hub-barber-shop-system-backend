from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.schedule import (
    ScheduleCreateDTO,
    ScheduleOutDTO,
    ScheduleUpdateDTO,
)
from src.domain.service.schedule import ScheduleService

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
async def test_schedule_service_create_delegates_to_repository():
    repo = AsyncMock()
    service = ScheduleService(repo)
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

    repo.list_schedules.assert_awaited_once_with(pagination, company_id)
    assert result == []


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
