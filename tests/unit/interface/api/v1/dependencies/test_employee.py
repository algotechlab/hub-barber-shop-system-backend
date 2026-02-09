import pytest
from src.interface.api.v1.controller.employee import EmployeeController
from src.interface.api.v1.dependencies.employee import get_employee_controller

pytestmark = pytest.mark.unit


class DummySession:
    pass


@pytest.mark.asyncio
async def test_get_employee_controller_returns_instance():
    session = DummySession()

    controller = await get_employee_controller(session)

    assert isinstance(controller, EmployeeController)
