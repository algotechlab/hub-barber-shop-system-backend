import pytest
from src.interface.api.v1.controller.analytics import AnalyticsController
from src.interface.api.v1.dependencies.analytics import get_analytics_controller

pytestmark = pytest.mark.unit


class DummySession:
    pass


@pytest.mark.asyncio
async def test_get_analytics_controller_returns_instance():
    session = DummySession()

    controller = await get_analytics_controller(session)

    assert isinstance(controller, AnalyticsController)
