from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.market_paid import MarketPaidCreateDTO
from src.infrastructure.repositories.market_paid_postgres import (
    MarketPaidRepositoryPostgres,
)


@pytest.mark.unit
class TestMarketPaidRepositoryPostgres:
    @pytest.fixture
    def session(self):
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def repo(self, session):
        return MarketPaidRepositoryPostgres(session)

    async def test_search_preapproval_plans_raises_not_implemented(self, repo):
        with pytest.raises(NotImplementedError):
            await repo.search_preapproval_plans(company_id=uuid4(), offset=0, limit=10)

    async def test_get_market_paid_by_company_id_returns_none(self, repo, session):
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        response = await repo.get_market_paid_by_company_id(uuid4())

        assert response is None
        session.execute.assert_awaited_once()

    async def test_get_market_paid_by_company_id_returns_dto(self, repo, session):
        market_paid = MagicMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = market_paid
        session.execute.return_value = result
        expected = MagicMock()

        with patch(
            'src.infrastructure.repositories.market_paid_postgres.MarketPaidOutDTO.model_validate',
            return_value=expected,
        ) as model_validate:
            response = await repo.get_market_paid_by_company_id(uuid4())

        model_validate.assert_called_once_with(market_paid, from_attributes=True)
        assert response == expected

    async def test_get_market_paid_by_company_id_raises_database_exception(
        self, repo, session
    ):
        session.execute.side_effect = RuntimeError('boom')

        with pytest.raises(DatabaseException):
            await repo.get_market_paid_by_company_id(uuid4())

        session.rollback.assert_awaited_once()

    async def test_create_market_paid_returns_dto(self, repo, session):
        payload = MarketPaidCreateDTO(
            company_id=uuid4(),
            public_key='public',
            access_token='access',
            market_paid_acess_token='mp_access',
            client_id='client',
            client_secret='secret',
        )
        expected = MagicMock()

        with patch(
            'src.infrastructure.repositories.market_paid_postgres.MarketPaidOutDTO.model_validate',
            return_value=expected,
        ) as model_validate:
            response = await repo.create_market_paid(payload)

        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once()
        model_validate.assert_called_once()
        assert response == expected

    async def test_create_market_paid_raises_database_exception(self, repo, session):
        payload = MarketPaidCreateDTO(
            company_id=uuid4(),
            public_key='public',
            access_token='access',
            market_paid_acess_token='mp_access',
            client_id='client',
            client_secret='secret',
        )
        session.commit.side_effect = RuntimeError('boom')

        with pytest.raises(DatabaseException):
            await repo.create_market_paid(payload)

        session.rollback.assert_awaited_once()

    async def test_get_market_paid_returns_none(self, repo, session):
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        response = await repo.get_market_paid(uuid4())

        assert response is None

    async def test_get_market_paid_returns_dto(self, repo, session):
        market_paid = MagicMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = market_paid
        session.execute.return_value = result
        expected = MagicMock()

        with patch(
            'src.infrastructure.repositories.market_paid_postgres.MarketPaidOutDTO.model_validate',
            return_value=expected,
        ) as model_validate:
            response = await repo.get_market_paid(uuid4())

        model_validate.assert_called_once_with(market_paid, from_attributes=True)
        assert response == expected

    async def test_get_market_paid_raises_database_exception(self, repo, session):
        session.execute.side_effect = RuntimeError('boom')

        with pytest.raises(DatabaseException):
            await repo.get_market_paid(uuid4())

        session.rollback.assert_awaited_once()
