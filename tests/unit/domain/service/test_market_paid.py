from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.market_paid import PreapprovalPlanSearchResponseDTO
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

        result = await service.search_preapproval_plans(offset=5, limit=2)

        mock_repository.search_preapproval_plans.assert_awaited_once_with(
            offset=5, limit=2
        )
        assert result == expected
