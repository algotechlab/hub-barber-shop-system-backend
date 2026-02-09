from unittest.mock import AsyncMock

import pytest
from src.interface.api.v1.controller.market_paid import MarketPaidController
from src.interface.api.v1.dependencies.market_paid import get_market_paid_controller
from src.interface.api.v1.schema.market_paid import PreapprovalPlanSearchResponseSchema
from src.main import app

URL_MARKET_PAID = '/api/v1/market-paid/preapproval-plans'


@pytest.fixture
def override_dependency_market_paid():
    mock_controller = AsyncMock(spec=MarketPaidController)

    def override_get_market_paid_controller():
        return mock_controller

    app.dependency_overrides[get_market_paid_controller] = (
        override_get_market_paid_controller
    )
    yield mock_controller
    app.dependency_overrides.clear()


def _assert_status(response, expected: int, msg_prefix: str = ''):
    if response.status_code != expected:
        body = response.json() if response.content else response.text
        raise AssertionError(
            f'{msg_prefix}Expected status {expected}, '
            f'got {response.status_code}. Body: {body}'
        )


@pytest.mark.unit
class TestMarketPaidRoutes:
    def test_search_preapproval_plans_returns_200(
        self, client, override_dependency_market_paid
    ):
        expected = PreapprovalPlanSearchResponseSchema(
            paging={'offset': 1, 'limit': 2, 'total': 0},
            results=[],
        )
        override_dependency_market_paid.search_preapproval_plans.return_value = expected

        response = client.get(f'{URL_MARKET_PAID}?offset=1&limit=2')

        _assert_status(response, 200)
        assert response.json()['paging']['offset'] == 1
        override_dependency_market_paid.search_preapproval_plans.assert_awaited_once_with(
            offset=1, limit=2
        )
