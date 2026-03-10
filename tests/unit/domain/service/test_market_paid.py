from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.market_paid import (
    MarketPaidCreateDTO,
    MarketPaidOutDTO,
    PreapprovalPlanSearchResponseDTO,
)
from src.domain.service.market_paid import MarketPaidService


@pytest.mark.unit
class TestMarketPaidService:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository):
        return MarketPaidService(market_paid_repository=mock_repository)

    async def test_search_preapproval_plans_delegates_to_repository(
        self, service, mock_repository
    ):
        expected = PreapprovalPlanSearchResponseDTO(
            paging={'offset': 0, 'limit': 10, 'total': 0},
            results=[],
        )
        mock_repository.search_preapproval_plans.return_value = expected

        company_id = uuid4()
        result = await service.search_preapproval_plans(
            company_id=company_id, offset=5, limit=2
        )

        mock_repository.search_preapproval_plans.assert_awaited_once_with(
            company_id=company_id, offset=5, limit=2
        )
        assert result == expected

    async def test_create_market_paid_delegates_to_repository(
        self, service, mock_repository
    ):
        payload = MarketPaidCreateDTO(
            company_id=uuid4(),
            public_key='public',
            access_token='access',
            market_paid_acess_token='mp_access',
            client_id='client',
            client_secret='secret',
        )
        expected = AsyncMock()
        mock_repository.create_market_paid.return_value = expected

        result = await service.create_market_paid(payload)

        mock_repository.create_market_paid.assert_awaited_once_with(payload)
        assert result == expected

    async def test_get_market_paid_delegates_to_repository(
        self, service, mock_repository
    ):
        expected = AsyncMock(spec=MarketPaidOutDTO)
        market_paid_id = uuid4()
        mock_repository.get_market_paid.return_value = expected

        result = await service.get_market_paid(market_paid_id)

        mock_repository.get_market_paid.assert_awaited_once_with(market_paid_id)
        assert result == expected
