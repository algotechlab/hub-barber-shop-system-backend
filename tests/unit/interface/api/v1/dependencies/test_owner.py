import pytest
from src.interface.api.v1.controller.owner import OwnerController
from src.interface.api.v1.dependencies.owner import get_owner_controller

pytestmark = pytest.mark.unit


class DummySession:
    pass


@pytest.mark.asyncio
async def test_get_owner_controller_returns_instance():
    session = DummySession()

    controller = await get_owner_controller(session)

    assert isinstance(controller, OwnerController)
