from unittest.mock import AsyncMock

import pytest
from src.interface.api.v1.controller.cash_register import CashRegisterController
from src.interface.api.v1.dependencies.cash_register import (
    get_cash_register_controller,
)


@pytest.mark.unit
async def test_get_cash_register_controller_returns_instance():
    session = AsyncMock()

    controller = await get_cash_register_controller(session)

    assert isinstance(controller, CashRegisterController)
