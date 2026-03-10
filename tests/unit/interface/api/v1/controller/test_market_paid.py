from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from src.domain.dtos.market_paid import (
    MarketPaidOutDTO,
    PreapprovalPlanSearchResponseDTO,
)
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
            company_id = uuid4()
            result = await controller.search_preapproval_plans(
                company_id=company_id, offset=1, limit=2
            )

        mock_use_case.search_preapproval_plans.assert_awaited_once_with(
            company_id=company_id, offset=1, limit=2
        )
        mv.assert_called_once_with(dto.model_dump())
        assert result == expected_schema

    async def test_create_market_paid_maps_input_and_returns_schema(
        self, controller, mock_use_case
    ):
        payload = {
            'company_id': uuid4(),
            'public_key': 'public',
            'access_token': 'access',
            'market_paid_acess_token': 'mp_access',
            'client_id': 'client',
            'client_secret': 'secret',
        }
        dto = MarketPaidOutDTO(
            id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted=False,
            **payload,
        )
        mock_use_case.create_market_paid.return_value = dto

        result = await controller.create_market_paid(
            MagicMock(model_dump=lambda: payload)
        )

        mock_use_case.create_market_paid.assert_awaited_once()
        assert result.id == dto.id
        assert result.company_id == dto.company_id

    async def test_get_market_paid_returns_schema(self, controller, mock_use_case):
        market_paid_id = uuid4()
        dto = MarketPaidOutDTO(
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
        mock_use_case.get_market_paid.return_value = dto

        result = await controller.get_market_paid(market_paid_id)

        mock_use_case.get_market_paid.assert_awaited_once_with(market_paid_id)
        assert result.id == dto.id
