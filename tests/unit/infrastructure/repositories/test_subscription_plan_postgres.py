from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.subscription_plan import (
    SubscriptionPlanCreateDTO,
    SubscriptionPlanOutDTO,
    SubscriptionPlanUpdateDTO,
)
from src.infrastructure.repositories.subscription_plan_postgres import (
    SubscriptionPlanRepositoryPostgres,
)


@pytest.mark.unit
class TestSubscriptionPlanRepositoryPostgres:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session):
        return SubscriptionPlanRepositoryPostgres(session=mock_session)

    async def test_service_belongs_to_company_true(self, repo, mock_session):
        mock_r = MagicMock()
        mock_r.scalar_one_or_none.return_value = object()
        mock_session.execute = AsyncMock(return_value=mock_r)
        assert await repo.service_belongs_to_company(uuid4(), uuid4()) is True

    async def test_service_belongs_to_company_false(self, repo, mock_session):
        mock_r = MagicMock()
        mock_r.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_r)
        assert await repo.service_belongs_to_company(uuid4(), uuid4()) is False

    async def test_service_belongs_rollback(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('e'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='e'):
            await repo.service_belongs_to_company(uuid4(), uuid4())
        mock_session.rollback.assert_awaited_once()

    async def test_create_plan_success(self, repo, mock_session):
        cid, sid = uuid4(), uuid4()
        dto = SubscriptionPlanCreateDTO(
            company_id=cid, service_id=sid, name='A', price=Decimal('1')
        )
        mock_orm = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        with patch(
            'src.infrastructure.repositories.subscription_plan_postgres.SubscriptionPlan',
            return_value=mock_orm,
        ) as pcls:
            with patch.object(
                SubscriptionPlanOutDTO, 'model_validate', return_value=MagicMock()
            ):
                await repo.create_plan(dto)
        pcls.assert_called_once()
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()

    async def test_create_plan_rollback_on_error(self, repo, mock_session):
        cid, sid = uuid4(), uuid4()
        dto = SubscriptionPlanCreateDTO(
            company_id=cid, service_id=sid, name='A', price=Decimal('1')
        )
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock(side_effect=RuntimeError('commit fail'))
        mock_session.rollback = AsyncMock()
        with patch(
            'src.infrastructure.repositories.subscription_plan_postgres.SubscriptionPlan',
            return_value=MagicMock(),
        ):
            with pytest.raises(DatabaseException, match='commit fail'):
                await repo.create_plan(dto)
        mock_session.rollback.assert_awaited_once()

    async def test_get_plan_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('query fail'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='query fail'):
            await repo.get_plan(uuid4(), uuid4())
        mock_session.rollback.assert_awaited_once()

    async def test_get_plan_with_active_only(self, repo, mock_session):
        mock_orm = MagicMock()
        mock_r = MagicMock()
        mock_r.scalar_one_or_none.return_value = mock_orm
        mock_session.execute = AsyncMock(return_value=mock_r)
        with patch.object(
            SubscriptionPlanOutDTO, 'model_validate', return_value=object()
        ):
            r = await repo.get_plan(uuid4(), uuid4(), active_only=True)
        assert r is not None

    async def test_get_plan_none(self, repo, mock_session):
        mock_r = MagicMock()
        mock_r.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_r)
        assert await repo.get_plan(uuid4(), uuid4()) is None

    async def test_list_plans_with_filter_name(self, repo, mock_session):
        mock_session.execute = AsyncMock(
            return_value=MagicMock(
                scalars=MagicMock(
                    return_value=MagicMock(all=MagicMock(return_value=[]))
                )
            )
        )
        p = PaginationParamsDTO(filter_by='name', filter_value='x', limit=5)
        r = await repo.list_plans(p, uuid4(), active_only=True)
        assert r == []

    async def test_list_plans_rollback(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=RuntimeError('db'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='db'):
            await repo.list_plans(PaginationParamsDTO(), uuid4())
        mock_session.rollback.assert_awaited_once()

    async def test_update_plan_empty_returns_get(self, repo, mock_session):
        pid, cid = uuid4(), uuid4()
        with patch.object(
            repo, 'get_plan', new_callable=AsyncMock, return_value=None
        ) as g:
            r = await repo.update_plan(pid, SubscriptionPlanUpdateDTO(), cid)
        g.assert_awaited_once_with(pid, cid)
        assert r is None

    async def test_update_plan_with_values(self, repo, mock_session):
        mock_r = MagicMock()
        mock_r.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_r)
        mock_session.commit = AsyncMock()
        with patch.object(
            SubscriptionPlanOutDTO, 'model_validate', return_value=object()
        ):
            r = await repo.update_plan(
                uuid4(),
                SubscriptionPlanUpdateDTO(name='B'),
                uuid4(),
            )
        assert r is not None

    async def test_update_plan_returns_none_when_no_row(self, repo, mock_session):
        mock_r = MagicMock()
        mock_r.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_r)
        mock_session.commit = AsyncMock()
        r = await repo.update_plan(
            uuid4(),
            SubscriptionPlanUpdateDTO(name='B'),
            uuid4(),
        )
        assert r is None

    async def test_update_plan_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('upd fail'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='upd fail'):
            await repo.update_plan(
                uuid4(),
                SubscriptionPlanUpdateDTO(name='B'),
                uuid4(),
            )
        mock_session.rollback.assert_awaited_once()

    async def test_delete_plan_true(self, repo, mock_session):
        mock_r = MagicMock()
        mock_r.rowcount = 1
        mock_session.execute = AsyncMock(return_value=mock_r)
        mock_session.commit = AsyncMock()
        assert await repo.delete_plan(uuid4(), uuid4()) is True

    async def test_delete_plan_rollback(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=OSError('x'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='x'):
            await repo.delete_plan(uuid4(), uuid4())
        mock_session.rollback.assert_awaited_once()
