from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from src.core.exceptions.custom import NotFoundException
from src.domain.dtos.market_paid import (
    MarketPaidCreateDTO,
    MarketPaidOutDTO,
    PreapprovalPlanSearchResponseDTO,
)
from src.infrastructure.repositories.market_paid_api import MarketPaidRepositoryApi


@pytest.mark.unit
class TestMarketPaidRepositoryApi:
    async def test_search_preapproval_plans_delegates_to_api(self):
        mock_api = AsyncMock()
        mock_postgres = AsyncMock()
        expected = PreapprovalPlanSearchResponseDTO(
            paging={'offset': 0, 'limit': 10, 'total': 0},
            results=[],
        )
        company_id = uuid4()
        mock_postgres.get_market_paid_by_company_id.return_value = MarketPaidOutDTO(
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
        mock_api.search_preapproval_plans.return_value = expected

        with (
            patch(
                'src.infrastructure.repositories.market_paid_api.MarketPaidApi',
                return_value=mock_api,
            ) as api_ctor,
            patch(
                'src.infrastructure.repositories.market_paid_api.MarketPaidRepositoryPostgres',
                return_value=mock_postgres,
            ) as postgres_ctor,
        ):
            repo = MarketPaidRepositoryApi(session=AsyncMock())
            result = await repo.search_preapproval_plans(
                company_id=company_id, offset=4, limit=5
            )

        api_ctor.assert_called_once_with()
        postgres_ctor.assert_called_once()
        mock_postgres.get_market_paid_by_company_id.assert_awaited_once_with(company_id)
        mock_api.search_preapproval_plans.assert_awaited_once_with(
            access_token='mp_access', offset=4, limit=5
        )
        assert result == expected

    async def test_search_preapproval_plans_raises_not_found_when_missing_credentials(
        self,
    ):
        mock_api = AsyncMock()
        mock_postgres = AsyncMock()
        company_id = uuid4()
        mock_postgres.get_market_paid_by_company_id.return_value = None

        with (
            patch(
                'src.infrastructure.repositories.market_paid_api.MarketPaidApi',
                return_value=mock_api,
            ),
            patch(
                'src.infrastructure.repositories.market_paid_api.MarketPaidRepositoryPostgres',
                return_value=mock_postgres,
            ),
        ):
            repo = MarketPaidRepositoryApi(session=AsyncMock())
            with pytest.raises(NotFoundException):
                await repo.search_preapproval_plans(company_id=company_id)

        mock_api.search_preapproval_plans.assert_not_called()

    async def test_create_market_paid_delegates_to_postgres(self):
        mock_postgres = AsyncMock()
        payload = MarketPaidCreateDTO(
            company_id=uuid4(),
            public_key='public',
            access_token='access',
            market_paid_acess_token='mp_access',
            client_id='client',
            client_secret='secret',
        )
        expected = AsyncMock(spec=MarketPaidOutDTO)
        mock_postgres.create_market_paid.return_value = expected

        with (
            patch(
                'src.infrastructure.repositories.market_paid_api.MarketPaidApi',
                return_value=AsyncMock(),
            ),
            patch(
                'src.infrastructure.repositories.market_paid_api.MarketPaidRepositoryPostgres',
                return_value=mock_postgres,
            ),
        ):
            repo = MarketPaidRepositoryApi(session=AsyncMock())
            result = await repo.create_market_paid(payload)

        mock_postgres.create_market_paid.assert_awaited_once_with(payload)
        assert result == expected

    async def test_get_market_paid_delegates_to_postgres(self):
        mock_postgres = AsyncMock()
        market_paid_id = uuid4()
        expected = AsyncMock(spec=MarketPaidOutDTO)
        mock_postgres.get_market_paid.return_value = expected

        with (
            patch(
                'src.infrastructure.repositories.market_paid_api.MarketPaidApi',
                return_value=AsyncMock(),
            ),
            patch(
                'src.infrastructure.repositories.market_paid_api.MarketPaidRepositoryPostgres',
                return_value=mock_postgres,
            ),
        ):
            repo = MarketPaidRepositoryApi(session=AsyncMock())
            result = await repo.get_market_paid(market_paid_id)

        mock_postgres.get_market_paid.assert_awaited_once_with(market_paid_id)
        assert result == expected
