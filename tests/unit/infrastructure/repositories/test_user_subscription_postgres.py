from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.user_subscription import (
    UserSubscriptionCreateDTO,
    UserSubscriptionOutDTO,
    UserSubscriptionWithPlanOutDTO,
)
from src.infrastructure.database.models.commom.user_subscription_status import (
    UserSubscriptionStatus,
)
from src.infrastructure.repositories.user_subscription_postgres import (
    UserSubscriptionRepositoryPostgres,
)


@pytest.mark.unit
class TestUserSubscriptionRepositoryPostgres:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session):
        return UserSubscriptionRepositoryPostgres(session=mock_session)

    def test_to_out_non_enum_status_string_path(self, repo):
        row = MagicMock()
        row.id = uuid4()
        row.user_id = uuid4()
        row.subscription_plan_id = uuid4()
        row.company_id = uuid4()
        row.status = 'ACTIVE'
        now = datetime.now(timezone.utc)
        row.started_at = now
        row.ended_at = None
        row.external_subscription_id = None
        row.created_at = now
        row.updated_at = now
        row.is_deleted = False
        o = UserSubscriptionRepositoryPostgres._to_out(row)
        assert o.status == 'ACTIVE'

    def test_to_out_enum_status(self, repo):
        row = MagicMock()
        row.id = uuid4()
        row.user_id = uuid4()
        row.subscription_plan_id = uuid4()
        row.company_id = uuid4()
        row.status = UserSubscriptionStatus.active
        now = datetime.now(timezone.utc)
        row.started_at = now
        row.ended_at = None
        row.external_subscription_id = None
        row.created_at = now
        row.updated_at = now
        row.is_deleted = False
        o = UserSubscriptionRepositoryPostgres._to_out(row)
        assert o.status == 'ACTIVE'

    async def test_has_active_for_plan(self, repo, mock_session):
        mock_r = MagicMock()
        mock_r.scalar_one_or_none.return_value = uuid4()
        mock_session.execute = AsyncMock(return_value=mock_r)
        assert await repo.has_active_for_plan(uuid4(), uuid4(), uuid4()) is True

    async def test_has_active_for_plan_rollback(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('e'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='e'):
            await repo.has_active_for_plan(uuid4(), uuid4(), uuid4())
        mock_session.rollback.assert_awaited_once()

    async def test_list_by_user(self, repo, mock_session):
        us = MagicMock()
        us.id = uuid4()
        us.user_id = uuid4()
        us.subscription_plan_id = uuid4()
        us.company_id = uuid4()
        us.status = UserSubscriptionStatus.active
        now = datetime.now(timezone.utc)
        us.started_at = now
        us.ended_at = None
        us.external_subscription_id = None
        us.created_at = now
        us.updated_at = now
        us.is_deleted = False

        row_tuple = (us, 'Plano A', Decimal('10'), uuid4(), 2)
        mock_r = MagicMock()
        mock_r.all.return_value = [row_tuple]
        mock_session.execute = AsyncMock(return_value=mock_r)
        r = await repo.list_by_user(PaginationParamsDTO(), uuid4(), us.user_id)
        assert len(r) == 1
        assert isinstance(r[0], UserSubscriptionWithPlanOutDTO)
        assert r[0].plan_name == 'Plano A'

    async def test_list_by_user_rollback(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('e'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='e'):
            await repo.list_by_user(PaginationParamsDTO(), uuid4(), uuid4())
        mock_session.rollback.assert_awaited_once()

    async def test_create_rollback_on_error(self, repo, mock_session):
        mock_session.add = MagicMock(side_effect=ValueError('fail'))
        mock_session.rollback = AsyncMock()
        dto = UserSubscriptionCreateDTO(
            user_id=uuid4(), company_id=uuid4(), subscription_plan_id=uuid4()
        )
        with pytest.raises(DatabaseException, match='fail'):
            await repo.create(dto)
        mock_session.rollback.assert_awaited_once()

    async def test_create_rollback_when_commit_fails(self, repo, mock_session):
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock(side_effect=RuntimeError('commit err'))
        mock_session.rollback = AsyncMock()
        dto = UserSubscriptionCreateDTO(
            user_id=uuid4(), company_id=uuid4(), subscription_plan_id=uuid4()
        )
        with pytest.raises(DatabaseException, match='commit err'):
            await repo.create(dto)
        mock_session.rollback.assert_awaited_once()

    async def test_create_success_commits_refreshes_and_returns(
        self, repo, mock_session
    ):
        uid, cid, pid = uuid4(), uuid4(), uuid4()
        dto = UserSubscriptionCreateDTO(
            user_id=uid, company_id=cid, subscription_plan_id=pid
        )
        now = datetime.now(timezone.utc)
        row = MagicMock()
        row.id = uuid4()
        row.user_id = uid
        row.subscription_plan_id = pid
        row.company_id = cid
        row.status = UserSubscriptionStatus.active
        row.started_at = now
        row.ended_at = None
        row.external_subscription_id = None
        row.created_at = now
        row.updated_at = now
        row.is_deleted = False
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        expected = UserSubscriptionOutDTO(
            id=row.id,
            user_id=uid,
            subscription_plan_id=pid,
            company_id=cid,
            status='ACTIVE',
            started_at=row.started_at,
            ended_at=None,
            external_subscription_id=None,
            created_at=row.created_at,
            updated_at=row.updated_at,
            is_deleted=False,
        )
        with patch(
            'src.infrastructure.repositories.user_subscription_postgres.UserSubscriptionModel',
            return_value=row,
        ):
            with patch.object(
                UserSubscriptionRepositoryPostgres, '_to_out', return_value=expected
            ):
                r = await repo.create(dto)
        assert r == expected
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(row)
