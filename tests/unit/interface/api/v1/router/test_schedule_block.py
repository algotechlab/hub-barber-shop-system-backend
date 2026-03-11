import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import Request
from src.interface.api.v1.controller.schedule_block import ScheduleBlockController
from src.interface.api.v1.dependencies.common.auth import require_current_employee
from src.interface.api.v1.dependencies.schedule_block import (
    get_schedule_block_controller,
)
from src.interface.api.v1.schema.schedule_block import (
    CreateScheduleBlockSchema,
    UpdateScheduleBlockSchema,
)
from src.main import app

URL_SCHEDULE_BLOCKS = '/api/v1/schedule-blocks'
STATUS_CODE_200 = 200
STATUS_CODE_201 = 201
STATUS_CODE_204 = 204


def _install_overrides() -> AsyncMock:
    mock_controller = AsyncMock(spec=ScheduleBlockController)

    def override_schedule_block_controller():
        return mock_controller

    app.dependency_overrides[get_schedule_block_controller] = (
        override_schedule_block_controller
    )

    async def override_require_current_employee(request: Request):
        request.state.company_id = uuid.uuid4()
        request.state.employee_id = uuid.uuid4()
        return request.state.employee_id

    app.dependency_overrides[require_current_employee] = (
        override_require_current_employee
    )
    return mock_controller


@pytest.fixture
def override_dependency_schedule_blocks():
    mock_controller = _install_overrides()
    yield mock_controller
    app.dependency_overrides.clear()


@pytest.mark.unit
class TestScheduleBlockRoutes:
    def test_create_schedule_block_returns_201(
        self, client, override_dependency_schedule_blocks
    ):
        payload = CreateScheduleBlockSchema(
            employee_id=uuid.uuid4(),
            start_time='2026-03-01T10:00:00Z',
            end_time='2026-03-01T11:00:00Z',
        )
        override_dependency_schedule_blocks.create_schedule_block.return_value = {
            'id': str(uuid.uuid4()),
            'employee_id': str(payload.employee_id),
            'start_time': '2026-03-01T10:00:00Z',
            'end_time': '2026-03-01T11:00:00Z',
            'created_at': '2026-03-01T09:00:00Z',
            'updated_at': '2026-03-01T09:00:00Z',
        }

        response = client.post(
            URL_SCHEDULE_BLOCKS, json=payload.model_dump(mode='json')
        )

        assert response.status_code == STATUS_CODE_201, response.json()
        assert response.json()['employee_id'] == str(payload.employee_id)

    def test_get_schedule_block_returns_200(
        self, client, override_dependency_schedule_blocks
    ):
        block_id = uuid.uuid4()
        override_dependency_schedule_blocks.get_schedule_block.return_value = {
            'id': str(block_id),
            'employee_id': str(uuid.uuid4()),
            'start_time': '2026-03-01T10:00:00Z',
            'end_time': '2026-03-01T11:00:00Z',
            'created_at': '2026-03-01T09:00:00Z',
            'updated_at': '2026-03-01T09:00:00Z',
        }

        response = client.get(f'{URL_SCHEDULE_BLOCKS}/{block_id}')

        assert response.status_code == STATUS_CODE_200, response.json()
        assert response.json()['id'] == str(block_id)

    def test_update_schedule_block_returns_200(
        self, client, override_dependency_schedule_blocks
    ):
        block_id = uuid.uuid4()
        payload = UpdateScheduleBlockSchema(
            start_time='2026-03-01T12:00:00Z',
            end_time='2026-03-01T13:00:00Z',
        )
        override_dependency_schedule_blocks.update_schedule_block.return_value = {
            'id': str(block_id),
            'employee_id': str(uuid.uuid4()),
            'start_time': '2026-03-01T12:00:00Z',
            'end_time': '2026-03-01T13:00:00Z',
            'created_at': '2026-03-01T09:00:00Z',
            'updated_at': '2026-03-01T09:30:00Z',
        }

        response = client.patch(
            f'{URL_SCHEDULE_BLOCKS}/{block_id}',
            json=payload.model_dump(mode='json', exclude_none=True),
        )

        assert response.status_code == STATUS_CODE_200, response.json()
        assert response.json()['id'] == str(block_id)

    def test_list_schedule_blocks_returns_200(
        self, client, override_dependency_schedule_blocks
    ):
        override_dependency_schedule_blocks.list_schedule_blocks.return_value = []
        response = client.get(URL_SCHEDULE_BLOCKS)
        assert response.status_code == STATUS_CODE_200, response.json()
        assert response.json() == []

    def test_delete_schedule_block_returns_204(
        self, client, override_dependency_schedule_blocks
    ):
        override_dependency_schedule_blocks.delete_schedule_block.return_value = True

        response = client.delete(f'{URL_SCHEDULE_BLOCKS}/{uuid.uuid4()}')

        assert response.status_code == STATUS_CODE_204, response.json()
