import pytest
from src.interface.api.v1.controller.schedule import ScheduleController
from src.interface.api.v1.dependencies.schedule import get_schedule_controller

pytestmark = pytest.mark.unit


class DummySession:
    pass


@pytest.mark.asyncio
async def test_get_schedule_controller_returns_instance():
    session = DummySession()

    controller = await get_schedule_controller(session)

    assert isinstance(controller, ScheduleController)
