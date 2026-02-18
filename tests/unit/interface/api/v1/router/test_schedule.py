import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import Request
from src.interface.api.v1.controller.schedule import ScheduleController
from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee_or_user,
)
from src.interface.api.v1.dependencies.schedule import get_schedule_controller
from src.interface.api.v1.schema.schedule import (
    CreateScheduleSchema,
    ScheduleOutSchema,
    UpdateScheduleSchema,
)
from src.main import app

URL_SCHEDULES = '/api/v1/schedule'
STATUS_CODE_200 = 200
STATUS_CODE_201 = 201
STATUS_CODE_204 = 204


def _install_overrides() -> AsyncMock:
    mock_controller = AsyncMock(spec=ScheduleController)

    def override_schedule_controller():
        return mock_controller

    app.dependency_overrides[get_schedule_controller] = override_schedule_controller

    async def override_require_current_employee_or_user(request: Request):
        request.state.company_id = uuid.uuid4()
        request.state.employee_id = uuid.uuid4()
        return request.state.employee_id

    app.dependency_overrides[require_current_employee_or_user] = (
        override_require_current_employee_or_user
    )
    return mock_controller


@pytest.fixture
def override_dependency_schedules():
    mock_controller = _install_overrides()
    yield mock_controller
    app.dependency_overrides.clear()


@pytest.mark.unit
class TestScheduleRoutes:
    def test_list_schedules_returns_200(self, client, override_dependency_schedules):
        schedule = ScheduleOutSchema(id=uuid.uuid4(), user_id=uuid.uuid4())
        override_dependency_schedules.list_schedules.return_value = [schedule]

        response = client.get(URL_SCHEDULES)

        assert response.status_code == STATUS_CODE_200, response.json()
        assert len(response.json()) == 1

    def test_create_schedule_returns_201(self, client, override_dependency_schedules):
        schedule = ScheduleOutSchema(id=uuid.uuid4(), user_id=uuid.uuid4())
        override_dependency_schedules.create_schedule.return_value = schedule

        payload = CreateScheduleSchema(
            user_id=schedule.user_id,
            service_id=uuid.uuid4(),
            product_id=uuid.uuid4(),
            employee_id=uuid.uuid4(),
            time_register=datetime(2026, 2, 14, 20, 6, 18),
            time_start=None,
            time_end=None,
            status=True,
            is_canceled=False,
        ).model_dump(mode='json')

        response = client.post(URL_SCHEDULES, json=payload)

        assert response.status_code == STATUS_CODE_201, response.json()
        assert response.json()['id'] == str(schedule.id)

    def test_get_schedule_returns_200(self, client, override_dependency_schedules):
        schedule = ScheduleOutSchema(id=uuid.uuid4(), user_id=uuid.uuid4())
        override_dependency_schedules.get_schedule.return_value = schedule

        response = client.get(f'{URL_SCHEDULES}/{uuid.uuid4()}')

        assert response.status_code == STATUS_CODE_200, response.json()
        assert response.json()['id'] == str(schedule.id)

    def test_update_schedule_returns_200(self, client, override_dependency_schedules):
        schedule = ScheduleOutSchema(id=uuid.uuid4(), user_id=uuid.uuid4())
        override_dependency_schedules.update_schedule.return_value = schedule

        payload = UpdateScheduleSchema(status=False).model_dump(
            mode='json', exclude_none=True
        )
        response = client.patch(f'{URL_SCHEDULES}/{uuid.uuid4()}', json=payload)

        assert response.status_code == STATUS_CODE_200, response.json()
        assert response.json()['id'] == str(schedule.id)

    def test_delete_schedule_returns_204(self, client, override_dependency_schedules):
        override_dependency_schedules.delete_schedule.return_value = None

        response = client.delete(f'{URL_SCHEDULES}/{uuid.uuid4()}')

        assert response.status_code == STATUS_CODE_204, response.text
