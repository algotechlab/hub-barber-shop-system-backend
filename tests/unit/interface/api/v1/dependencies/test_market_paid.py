from unittest.mock import patch

import pytest
from src.interface.api.v1.dependencies.market_paid import get_market_paid_controller

pytestmark = pytest.mark.unit


async def test_get_market_paid_controller_wires_dependencies():
    fake_repo = object()
    fake_service = object()
    fake_use_case = object()
    fake_controller = object()

    with (
        patch(
            'src.interface.api.v1.dependencies.market_paid.MarketPaidRepositoryApi',
            return_value=fake_repo,
        ) as repo_ctor,
        patch(
            'src.interface.api.v1.dependencies.market_paid.MarketPaidService',
            return_value=fake_service,
        ) as service_ctor,
        patch(
            'src.interface.api.v1.dependencies.market_paid.MarketPaidUseCase',
            return_value=fake_use_case,
        ) as use_case_ctor,
        patch(
            'src.interface.api.v1.dependencies.market_paid.MarketPaidController',
            return_value=fake_controller,
        ) as controller_ctor,
    ):
        controller = await get_market_paid_controller()

    assert controller is fake_controller
    repo_ctor.assert_called_once_with()
    service_ctor.assert_called_once_with(fake_repo)
    use_case_ctor.assert_called_once_with(fake_service)
    controller_ctor.assert_called_once_with(fake_use_case)
