from unittest.mock import Mock

import pytest
from src.interface.api.v1.controller.product import ProductController
from src.interface.api.v1.dependencies.product import get_product_controller

pytestmark = pytest.mark.unit


class DummySession:
    pass


@pytest.mark.asyncio
async def test_get_product_controller_returns_instance(monkeypatch):
    monkeypatch.setattr(
        'src.interface.api.v1.dependencies.product.S3Storage.from_settings',
        Mock(return_value=Mock()),
    )
    session = DummySession()

    controller = await get_product_controller(session)

    assert isinstance(controller, ProductController)
