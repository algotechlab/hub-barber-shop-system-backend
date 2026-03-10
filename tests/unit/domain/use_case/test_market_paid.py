from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.market_paid import (
    MarketPaidCreateDTO,
    MarketPaidOutDTO,
    PreapprovalPlanSearchResponseDTO,
)
from src.domain.use_case.market_paid import MarketPaidUseCase


@pytest.mark.unit
class TestMarketPaidUseCase:
    @pytest.fixture
    def mock_service(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_service):
        return MarketPaidUseCase(market_paid_service=mock_service)

    async def test_search_preapproval_plans_delegates_to_service(
        self, use_case, mock_service
    ):
        expected = PreapprovalPlanSearchResponseDTO(
            paging={'offset': 0, 'limit': 10, 'total': 0},
            results=[],
        )
        mock_service.search_preapproval_plans.return_value = expected

        company_id = uuid4()
        result = await use_case.search_preapproval_plans(
            company_id=company_id, offset=3, limit=7
        )

        mock_service.search_preapproval_plans.assert_awaited_once_with(
            company_id=company_id, offset=3, limit=7
        )
        assert result == expected

    async def test_create_market_paid_delegates_to_service(
        self, use_case, mock_service
    ):
        payload = MarketPaidCreateDTO(
            company_id=uuid4(),
            public_key='public',
            access_token='access',
            market_paid_acess_token='mp_access',
            client_id='client',
            client_secret='secret',
        )
        expected = AsyncMock(spec=MarketPaidOutDTO)
        mock_service.create_market_paid.return_value = expected

        result = await use_case.create_market_paid(payload)

        mock_service.create_market_paid.assert_awaited_once_with(payload)
        assert result == expected

    async def test_get_market_paid_delegates_to_service(self, use_case, mock_service):
        market_paid_id = uuid4()
        expected = AsyncMock(spec=MarketPaidOutDTO)
        mock_service.get_market_paid.return_value = expected

        result = await use_case.get_market_paid(market_paid_id)

        mock_service.get_market_paid.assert_awaited_once_with(market_paid_id)
        assert result == expected
