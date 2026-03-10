from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.domain.dtos.market_paid import PreapprovalPlanSearchResponseDTO
from src.infrastructure.external_apis.market_paid import MarketPaidApi


@pytest.mark.unit
class TestMarketPaidApi:
    def test_init_calls_api_base_client_init(self):
        with (
            patch('src.infrastructure.external_apis.market_paid.settings') as settings,
            patch(
                'src.infrastructure.external_apis.market_paid.ApiBaseClient.__init__',
                return_value=None,
            ) as base_init,
        ):
            settings.MARKET_PAID_BASE_URL = 'https://example.com'
            MarketPaidApi()

        base_init.assert_called_once()

    async def test_search_preapproval_plans_builds_url_and_validates_response(self):
        with (
            patch('src.infrastructure.external_apis.market_paid.settings') as settings,
            patch(
                'src.infrastructure.external_apis.market_paid.ApiBaseClient.__init__',
                return_value=None,
            ),
        ):
            settings.MARKET_PAID_BASE_URL = 'https://example.com'
            api = MarketPaidApi()

        mock_response = MagicMock()
        payload = {'paging': {'offset': 1, 'limit': 2, 'total': 0}, 'results': []}
        mock_response.json.return_value = payload
        api.request = AsyncMock(return_value=mock_response)

        expected = MagicMock()
        with patch.object(
            PreapprovalPlanSearchResponseDTO,
            'model_validate',
            return_value=expected,
        ) as mv:
            result = await api.search_preapproval_plans(
                access_token='token', offset=1, limit=2
            )

        api.request.assert_awaited_once_with({
            'method': 'GET',
            'url': '/preapproval_plan/search?offset=1&limit=2',
            'headers': {'Authorization': 'Bearer token'},
        })
        mv.assert_called_once_with(payload)
        assert result == expected
