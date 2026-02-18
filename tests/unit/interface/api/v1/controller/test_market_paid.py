from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.domain.dtos.market_paid import PreapprovalPlanSearchResponseDTO
from src.interface.api.v1.controller.market_paid import MarketPaidController
from src.interface.api.v1.schema.market_paid import PreapprovalPlanSearchResponseSchema


@pytest.mark.unit
class TestMarketPaidController:
    @pytest.fixture
    def mock_use_case(self):
        return AsyncMock()

    @pytest.fixture
    def controller(self, mock_use_case):
        return MarketPaidController(market_paid_use_case=mock_use_case)

    async def test_search_preapproval_plans_returns_schema(
        self, controller, mock_use_case
    ):
        dto = PreapprovalPlanSearchResponseDTO(
            paging={'offset': 0, 'limit': 10, 'total': 0},
            results=[],
        )
        mock_use_case.search_preapproval_plans.return_value = dto

        expected_schema = MagicMock()
        with patch.object(
            PreapprovalPlanSearchResponseSchema,
            'model_validate',
            return_value=expected_schema,
        ) as mv:
            result = await controller.search_preapproval_plans(offset=1, limit=2)

        mock_use_case.search_preapproval_plans.assert_awaited_once_with(
            offset=1, limit=2
        )
        mv.assert_called_once_with(dto.model_dump())
        assert result == expected_schema
