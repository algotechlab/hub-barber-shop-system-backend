from unittest.mock import AsyncMock, patch

import pytest
from src.domain.dtos.market_paid import PreapprovalPlanSearchResponseDTO
from src.infrastructure.repositories.market_paid_api import MarketPaidRepositoryApi


@pytest.mark.unit
class TestMarketPaidRepositoryApi:
    async def test_search_preapproval_plans_delegates_to_api(self):
        mock_api = AsyncMock()
        expected = PreapprovalPlanSearchResponseDTO(
            paging={'offset': 0, 'limit': 10, 'total': 0},
            results=[],
        )
        mock_api.search_preapproval_plans.return_value = expected

        with patch(
            'src.infrastructure.repositories.market_paid_api.MarketPaidApi',
            return_value=mock_api,
        ) as api_ctor:
            repo = MarketPaidRepositoryApi()
            result = await repo.search_preapproval_plans(offset=4, limit=5)

        api_ctor.assert_called_once_with()
        mock_api.search_preapproval_plans.assert_awaited_once_with(offset=4, limit=5)
        assert result == expected
