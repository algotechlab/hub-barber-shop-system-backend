from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.market_paid import PreapprovalPlanSearchResponseDTO
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

        result = await use_case.search_preapproval_plans(offset=3, limit=7)

        mock_service.search_preapproval_plans.assert_awaited_once_with(
            offset=3, limit=7
        )
        assert result == expected
