import pytest
from src.interface.api.v1.controller.company import CompanyController
from src.interface.api.v1.dependencies.company import get_company_controller

pytestmark = pytest.mark.unit


class DummySession:
    pass


@pytest.mark.asyncio
async def test_get_company_controller_returns_instance():
    controller = await get_company_controller(DummySession())
    assert isinstance(controller, CompanyController)
