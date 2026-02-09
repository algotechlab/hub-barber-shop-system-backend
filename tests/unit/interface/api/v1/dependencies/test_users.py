import pytest
from src.interface.api.v1.controller.users import UsersController
from src.interface.api.v1.dependencies.users import get_users_controller

pytestmark = pytest.mark.unit


class DummySession:
    pass


@pytest.mark.asyncio
async def test_get_users_controller_returns_instance():
    session = DummySession()

    controller = await get_users_controller(session)

    assert isinstance(controller, UsersController)
