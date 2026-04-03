from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.schedule import ScheduleOutDTO
from src.infrastructure.repositories.marketing_inactive_postgres import (
    MarketingInactiveRepositoryPostgres,
    _days_since_last_visit,
    _since_utc_naive,
    _utc_naive_now,
)
from src.infrastructure.repositories.schedule_postgres import ScheduleRepositoryPostgres


@pytest.mark.unit
class TestMarketingInactiveHelpers:
    def test_utc_naive_now(self):
        assert _utc_naive_now().tzinfo is None

    def test_since_utc_naive(self):
        s = _since_utc_naive(2)
        assert s < _utc_naive_now()

    def test_days_since_last_visit_fallback(self):
        old = datetime(2020, 1, 1)
        recent = datetime(2024, 1, 1)
        assert _days_since_last_visit(None, old) > _days_since_last_visit(None, recent)

    def test_days_since_last_visit_tz_aware(self):
        past = datetime(2024, 6, 1, tzinfo=timezone.utc)
        fb = datetime(2025, 1, 1)
        d = _days_since_last_visit(past, fb)
        assert d >= 0


@pytest.mark.unit
class TestMarketingInactiveRepositoryPostgres:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.fixture
    def repo(self, mock_session):
        return MarketingInactiveRepositoryPostgres(mock_session)

    async def test_fetch_inactive_clients_raises(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=RuntimeError('db'))
        with pytest.raises(DatabaseException, match='db'):
            await repo.fetch_inactive_clients(uuid4())

    async def test_fetch_inactive_clients_success(self, repo, mock_session):
        company_id = uuid4()
        uid = uuid4()
        created = datetime(2022, 1, 1)

        u = SimpleNamespace(
            id=uid,
            name='U',
            email='u@u.com',
            phone='5511',
            company_id=company_id,
            is_active=True,
            created_at=created,
        )
        mock_user_result = MagicMock()
        mock_user_result.all.return_value = [(u, None)]

        sched = ScheduleOutDTO(
            id=uuid4(),
            user_id=uid,
            service_id=[uuid4()],
            employee_id=uuid4(),
            company_id=company_id,
            time_register=datetime.now(timezone.utc),
            is_confirmed=True,
            is_canceled=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_deleted=False,
        )

        mock_session.execute = AsyncMock(return_value=mock_user_result)

        with patch.object(
            repo,
            '_list_schedules_lookback',
            new_callable=AsyncMock,
            return_value=[sched],
        ):
            out = await repo.fetch_inactive_clients(company_id)

        assert len(out.users) == 1
        assert out.users[0].email == 'u@u.com'
        assert len(out.schedules) == 1

    async def test_fetch_filters_email_and_days(self, repo, mock_session):
        company_id = uuid4()
        uid = uuid4()
        created = datetime(2020, 1, 1)

        u = SimpleNamespace(
            id=uid,
            name='U',
            email='find@x.com',
            phone='5511',
            company_id=company_id,
            is_active=True,
            created_at=created,
        )
        mock_user_result = MagicMock()
        mock_user_result.all.return_value = [(u, None)]
        mock_session.execute = AsyncMock(return_value=mock_user_result)

        with patch.object(
            repo,
            '_list_schedules_lookback',
            new_callable=AsyncMock,
            return_value=[],
        ):
            out = await repo.fetch_inactive_clients(
                company_id,
                email='FIND',
                min_days=0,
                max_days=50000,
            )
        assert len(out.users) == 1

    async def test_fetch_min_days_excludes_user(self, repo, mock_session):
        company_id = uuid4()
        uid = uuid4()
        last_visit = datetime(2025, 6, 10, 12, 0, 0)
        u = SimpleNamespace(
            id=uid,
            name='U',
            email='u@u.com',
            phone='5511',
            company_id=company_id,
            is_active=True,
            created_at=datetime(2010, 1, 1),
        )
        mock_user_result = MagicMock()
        mock_user_result.all.return_value = [(u, last_visit)]
        mock_session.execute = AsyncMock(return_value=mock_user_result)
        with (
            patch(
                'src.infrastructure.repositories.marketing_inactive_postgres._utc_naive_now',
                return_value=datetime(2025, 6, 15, 12, 0, 0),
            ),
            patch.object(
                repo,
                '_list_schedules_lookback',
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            out = await repo.fetch_inactive_clients(company_id, min_days=100)
        assert len(out.users) == 0

    async def test_fetch_max_days_excludes_user(self, repo, mock_session):
        company_id = uuid4()
        uid = uuid4()
        last_visit = datetime(2020, 1, 1)
        u = SimpleNamespace(
            id=uid,
            name='U',
            email='u@u.com',
            phone='5511',
            company_id=company_id,
            is_active=True,
            created_at=datetime(2010, 1, 1),
        )
        mock_user_result = MagicMock()
        mock_user_result.all.return_value = [(u, last_visit)]
        mock_session.execute = AsyncMock(return_value=mock_user_result)
        with (
            patch(
                'src.infrastructure.repositories.marketing_inactive_postgres._utc_naive_now',
                return_value=datetime(2025, 6, 15, 12, 0, 0),
            ),
            patch.object(
                repo,
                '_list_schedules_lookback',
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            out = await repo.fetch_inactive_clients(company_id, max_days=5)
        assert len(out.users) == 0

    async def test_list_schedules_lookback(self, repo, mock_session):
        sched = ScheduleOutDTO(
            id=uuid4(),
            user_id=uuid4(),
            service_id=[uuid4()],
            employee_id=uuid4(),
            company_id=uuid4(),
            time_register=datetime(2024, 1, 1),
            is_confirmed=True,
            is_canceled=False,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
            is_deleted=False,
        )
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (MagicMock(), 'U', 'E', ['svc'], 'P', 30),
        ]
        mock_session.execute = AsyncMock(return_value=mock_result)
        with patch.object(
            ScheduleRepositoryPostgres,
            '_schedule_row_to_out_dto',
            return_value=sched,
        ):
            out = await repo._list_schedules_lookback(
                uuid4(), since=datetime(2020, 1, 1), limit=5
            )
        assert len(out) == 1
        assert out[0] is sched
