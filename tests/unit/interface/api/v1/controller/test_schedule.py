import uuid
from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.schedule import ScheduleOutDTO
from src.interface.api.v1.controller.schedule import ScheduleController
from src.interface.api.v1.schema.schedule import (
    CreateScheduleSchema,
    UpdateScheduleSchema,
)


@pytest.mark.unit
class TestScheduleController:
    @pytest.mark.asyncio
    async def test_list_schedules(self):
        company_id = uuid.uuid4()
        use_case = AsyncMock()
        use_case.list_schedules.return_value = [
            ScheduleOutDTO(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                service_id=uuid.uuid4(),
                product_id=uuid.uuid4(),
                employee_id=uuid.uuid4(),
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
        ]
        controller = ScheduleController(use_case)
        pagination = PaginationParamsDTO()

        result = await controller.list_schedules(pagination, company_id=company_id)

        assert len(result) == 1
        assert result[0].id is not None
        use_case.list_schedules.assert_awaited_once_with(pagination, company_id)

    @pytest.mark.asyncio
    async def test_create_schedule(self):
        company_id = uuid.uuid4()
        use_case = AsyncMock()
        created = ScheduleOutDTO(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            service_id=uuid.uuid4(),
            product_id=uuid.uuid4(),
            employee_id=uuid.uuid4(),
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
        use_case.create_schedule.return_value = created
        controller = ScheduleController(use_case)

        payload = CreateScheduleSchema(
            user_id=created.user_id,
            service_id=created.service_id,
            product_id=created.product_id,
            employee_id=created.employee_id,
            time_register='2026-02-14T20:06:18',
            time_start=None,
            time_end=None,
            status=True,
            is_canceled=False,
        )
        result = await controller.create_schedule(payload, company_id=company_id)

        assert result.id == created.id
        assert result.user_id == created.user_id

    @pytest.mark.asyncio
    async def test_get_schedule(self):
        company_id = uuid.uuid4()
        use_case = AsyncMock()
        schedule = ScheduleOutDTO(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            service_id=uuid.uuid4(),
            product_id=uuid.uuid4(),
            employee_id=uuid.uuid4(),
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
        use_case.get_schedule.return_value = schedule
        controller = ScheduleController(use_case)

        result = await controller.get_schedule(schedule.id, company_id=company_id)

        assert result.id == schedule.id

    @pytest.mark.asyncio
    async def test_update_schedule(self):
        company_id = uuid.uuid4()
        use_case = AsyncMock()
        updated = ScheduleOutDTO(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            service_id=uuid.uuid4(),
            product_id=uuid.uuid4(),
            employee_id=uuid.uuid4(),
            company_id=company_id,
            time_register='2026-02-14T20:06:18',
            time_start=None,
            time_end=None,
            status=False,
            is_canceled=False,
            created_at='2026-02-14T20:06:18',
            updated_at='2026-02-14T20:06:18',
            is_deleted=False,
        )
        use_case.update_schedule.return_value = updated
        controller = ScheduleController(use_case)

        payload = UpdateScheduleSchema(status=False)
        result = await controller.update_schedule(
            updated.id, payload, company_id=company_id
        )

        assert result.id == updated.id
        assert result.user_id == updated.user_id

    @pytest.mark.asyncio
    async def test_delete_schedule(self):
        use_case = AsyncMock()
        use_case.delete_schedule.return_value = True
        controller = ScheduleController(use_case)

        await controller.delete_schedule(uuid.uuid4(), company_id=uuid.uuid4())

        use_case.delete_schedule.assert_awaited_once()
