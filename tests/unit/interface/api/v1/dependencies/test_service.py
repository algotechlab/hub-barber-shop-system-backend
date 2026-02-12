from unittest.mock import Mock

import pytest
from src.interface.api.v1.controller.service import ServiceController
from src.interface.api.v1.dependencies.service import get_service_controller

pytestmark = pytest.mark.unit


class DummySession:
    pass


@pytest.mark.asyncio
async def test_get_service_controller_returns_instance(monkeypatch):
    monkeypatch.setattr(
        'src.interface.api.v1.dependencies.service.S3Storage.from_settings',
        Mock(return_value=Mock()),
    )
    session = DummySession()

    controller = await get_service_controller(session)

    assert isinstance(controller, ServiceController)
