import pytest
from src.interface.api.v1.controller.schedule_block import ScheduleBlockController
from src.interface.api.v1.dependencies.schedule_block import (
    get_schedule_block_controller,
)

pytestmark = pytest.mark.unit


class DummySession:
    pass


@pytest.mark.asyncio
async def test_get_schedule_block_controller_returns_instance():
    session = DummySession()

    controller = await get_schedule_block_controller(session)

    assert isinstance(controller, ScheduleBlockController)
