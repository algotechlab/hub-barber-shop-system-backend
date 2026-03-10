from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.interface.api.v1.controller.market_paid import MarketPaidController
from src.interface.api.v1.dependencies.market_paid import get_market_paid_controller
from src.interface.api.v1.schema.market_paid import (
    MarketPaidOutSchema,
    PreapprovalPlanSearchResponseSchema,
)
from src.main import app

URL_MARKET_PAID = '/api/v1/market-paid/preapproval-plans'
URL_MARKET_PAID_BASE = '/api/v1/market-paid'


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
        company_id = uuid4()
        expected = PreapprovalPlanSearchResponseSchema(
            paging={'offset': 1, 'limit': 2, 'total': 0},
            results=[],
        )
        override_dependency_market_paid.search_preapproval_plans.return_value = expected

        response = client.get(
            f'{URL_MARKET_PAID}?company_id={company_id}&offset=1&limit=2'
        )

        _assert_status(response, 200)
        assert response.json()['paging']['offset'] == 1
        override_dependency_market_paid.search_preapproval_plans.assert_awaited_once_with(
            company_id=company_id, offset=1, limit=2
        )

    def test_search_preapproval_plans_returns_422_without_company_id(
        self, client, override_dependency_market_paid
    ):
        response = client.get(f'{URL_MARKET_PAID}?offset=1&limit=2')

        _assert_status(response, 422)
        assert 'Informe o company_id' in response.json()['detail']
        override_dependency_market_paid.search_preapproval_plans.assert_not_called()

    def test_create_market_paid_returns_201(
        self, client, override_dependency_market_paid
    ):
        company_id = uuid4()
        payload = {
            'company_id': str(company_id),
            'public_key': 'public',
            'access_token': 'access',
            'market_paid_acess_token': 'mp_access',
            'client_id': 'client',
            'client_secret': 'secret',
        }
        created = MarketPaidOutSchema(
            id=uuid4(),
            company_id=company_id,
            public_key='public',
            access_token='access',
            market_paid_acess_token='mp_access',
            client_id='client',
            client_secret='secret',
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted=False,
        )
        override_dependency_market_paid.create_market_paid.return_value = created

        response = client.post(URL_MARKET_PAID_BASE, json=payload)

        _assert_status(response, 201)
        override_dependency_market_paid.create_market_paid.assert_awaited_once()

    def test_get_market_paid_returns_200(self, client, override_dependency_market_paid):
        market_paid_id = uuid4()
        expected = MarketPaidOutSchema(
            id=market_paid_id,
            company_id=uuid4(),
            public_key='public',
            access_token='access',
            market_paid_acess_token='mp_access',
            client_id='client',
            client_secret='secret',
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted=False,
        )
        override_dependency_market_paid.get_market_paid.return_value = expected

        response = client.get(f'{URL_MARKET_PAID_BASE}/{market_paid_id}')

        _assert_status(response, 200)
        override_dependency_market_paid.get_market_paid.assert_awaited_once_with(
            market_paid_id
        )
