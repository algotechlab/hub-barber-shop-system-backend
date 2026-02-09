import pytest
from src.interface.api.v1.controller.auth import AuthController
from src.interface.api.v1.dependencies.auth import get_auth_controller

pytestmark = pytest.mark.unit


class DummySession:
    pass


@pytest.mark.asyncio
async def test_get_auth_controller_returns_instance():
    session = DummySession()
    controller = await get_auth_controller(session)
    assert isinstance(controller, AuthController)
