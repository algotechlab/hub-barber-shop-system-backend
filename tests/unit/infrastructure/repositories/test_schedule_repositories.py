from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.schedule import (
    ScheduleCreateDTO,
    ScheduleOutDTO,
    ScheduleUpdateDTO,
    SlotsInDTO,
)
from src.infrastructure.repositories.schedule_postgres import ScheduleRepositoryPostgres


@pytest.mark.unit
class TestScheduleRepositoryPostgres:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session):
        return ScheduleRepositoryPostgres(session=mock_session)

    async def test_create_schedule_success(self, repo, mock_session):
        dto = ScheduleCreateDTO(
            user_id=uuid4(),
            service_id=uuid4(),
            product_id=uuid4(),
            employee_id=uuid4(),
            company_id=uuid4(),
            time_register=datetime(2026, 2, 14, 20, 6, 18),
            time_start=None,
            time_end=None,
            status=True,
            is_canceled=False,
        )
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_orm = MagicMock()

        expected = MagicMock(spec=ScheduleOutDTO)
        with (
            patch(
                'src.infrastructure.repositories.schedule_postgres.Schedule',
                return_value=mock_orm,
            ),
            patch.object(ScheduleOutDTO, 'model_validate', return_value=expected) as mv,
        ):
            result = await repo.create_schedule(dto)

        mock_session.add.assert_called_once_with(mock_orm)
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(mock_orm)
        mv.assert_called_once_with(mock_orm)
        assert result == expected

    async def test_create_schedule_rollback_on_error(self, repo, mock_session):
        mock_session.add = MagicMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()
        dto = ScheduleCreateDTO(
            user_id=uuid4(),
            service_id=uuid4(),
            product_id=uuid4(),
            employee_id=uuid4(),
            company_id=uuid4(),
            time_register=datetime(2026, 2, 14, 20, 6, 18),
            time_start=None,
            time_end=None,
            status=True,
            is_canceled=False,
        )

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.create_schedule(dto)

        mock_session.rollback.assert_awaited_once()

    async def test_list_schedules_success(self, repo, mock_session):
        mock_orm_schedules = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (
                mock_orm_schedules[0],
                'User 1',
                'Employee 1',
                'Service 1',
                'Product 1',
                30,
            ),
            (
                mock_orm_schedules[1],
                'User 2',
                'Employee 2',
                'Service 2',
                'Product 2',
                45,
            ),
        ]
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected = [MagicMock(), MagicMock()]
        with patch.object(ScheduleOutDTO, 'model_validate', side_effect=expected) as mv:
            result = await repo.list_schedules(PaginationParamsDTO(), uuid4())

        assert result == expected
        assert mv.call_count == len(mock_orm_schedules)

    async def test_list_schedules_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.list_schedules(PaginationParamsDTO(), uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_list_schedules_success_with_employee_filter(
        self, repo, mock_session
    ):
        employee_id = uuid4()
        mock_orm_schedules = [MagicMock()]
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (
                mock_orm_schedules[0],
                'User 1',
                'Employee 1',
                'Service 1',
                'Product 1',
                30,
            )
        ]
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected = [MagicMock()]
        with patch.object(ScheduleOutDTO, 'model_validate', side_effect=expected):
            result = await repo.list_schedules(
                PaginationParamsDTO(), uuid4(), employee_id=employee_id
            )

        mock_session.execute.assert_awaited_once()
        assert result == expected

    async def test_get_schedule_by_user_id_success(self, repo):
        pagination = PaginationParamsDTO()
        company_id = uuid4()
        user_id = uuid4()
        expected = [MagicMock()]

        with patch.object(
            repo, 'list_schedules', AsyncMock(return_value=expected)
        ) as list_schedules:
            result = await repo.get_schedule_by_user_id(pagination, company_id, user_id)

        list_schedules.assert_awaited_once_with(
            pagination=pagination,
            company_id=company_id,
            employee_id=None,
            user_id=user_id,
        )
        assert result == expected

    async def test_get_schedule_by_user_id_rollback_on_error(self, repo, mock_session):
        mock_session.rollback = AsyncMock()
        pagination = PaginationParamsDTO()

        with patch.object(
            repo, 'list_schedules', AsyncMock(side_effect=ValueError('DB error'))
        ):
            with pytest.raises(DatabaseException, match='DB error'):
                await repo.get_schedule_by_user_id(pagination, uuid4(), uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_get_slots_success(self, repo, mock_session):
        booked_schedule = MagicMock()
        booked_schedule.time_start = datetime(2026, 2, 14, 9, 15, 0)
        booked_schedule.time_end = datetime(2026, 2, 14, 9, 45, 0)
        mock_scalar_result = MagicMock()
        mock_scalar_result.all.return_value = [booked_schedule]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_session.execute = AsyncMock(return_value=mock_result)

        slots = SlotsInDTO(
            company_id=uuid4(),
            employee_id=uuid4(),
            work_start=datetime(2026, 2, 14, 9, 0, 0),
            work_end=datetime(2026, 2, 14, 10, 0, 0),
            slot_minutes=30,
            target_date=None,
        )
        result = await repo.get_slots(slots)
        result_range = 2
        assert len(result) == result_range
        assert result[0].is_blocked is True
        assert result[1].is_blocked is True

    async def test_get_slots_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()
        slots = SlotsInDTO(
            company_id=uuid4(),
            employee_id=uuid4(),
            work_start=datetime(2026, 2, 14, 9, 0, 0),
            work_end=datetime(2026, 2, 14, 10, 0, 0),
            slot_minutes=30,
            target_date=None,
        )

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_slots(slots)

        mock_session.rollback.assert_awaited_once()

    async def test_get_slots_blocks_using_target_date(self, repo, mock_session):
        booked_schedule = MagicMock()
        booked_schedule.time_start = datetime(2026, 3, 3, 13, 0, 0)
        booked_schedule.time_end = datetime(2026, 3, 3, 13, 30, 0)
        mock_scalar_result = MagicMock()
        mock_scalar_result.all.return_value = [booked_schedule]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_session.execute = AsyncMock(return_value=mock_result)

        slots = SlotsInDTO(
            company_id=uuid4(),
            employee_id=uuid4(),
            work_start=datetime(2026, 3, 1, 13, 0, 0),
            work_end=datetime(2026, 3, 1, 14, 0, 0),
            slot_minutes=30,
            target_date=datetime(2026, 3, 3, 0, 0, 0).date(),
        )

        result = await repo.get_slots(slots)
        result_range = 2
        assert len(result) == result_range
        assert result[0].time_start == datetime(2026, 3, 3, 13, 0, 0)
        assert result[0].is_blocked is True
        assert result[0].is_available is False
        assert result[1].is_blocked is False

    async def test_get_schedule_returns_none_when_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_schedule(uuid4(), uuid4())

        assert result is None

    async def test_get_schedule_success(self, repo, mock_session):
        mock_orm = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_orm
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected = MagicMock()
        with patch.object(
            ScheduleOutDTO, 'model_validate', return_value=expected
        ) as mv:
            result = await repo.get_schedule(uuid4(), uuid4())

        mv.assert_called_once_with(mock_orm)
        assert result == expected

    async def test_get_schedule_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_schedule(uuid4(), uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_block_schedule_returns_none_when_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.block_schedule(uuid4(), uuid4())

        assert result is None

    async def test_block_schedule_returns_true_when_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.block_schedule(uuid4(), uuid4())

        assert result is True

    async def test_block_schedule_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.block_schedule(uuid4(), uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_update_schedule_returns_none_when_not_found(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.update_schedule(
            uuid4(), ScheduleUpdateDTO(status=False), uuid4()
        )

        assert result is None
        mock_session.commit.assert_awaited_once()

    async def test_update_schedule_success(self, repo, mock_session):
        mock_updated = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_updated
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        expected = MagicMock()
        with patch.object(
            ScheduleOutDTO, 'model_validate', return_value=expected
        ) as mv:
            result = await repo.update_schedule(
                uuid4(), ScheduleUpdateDTO(status=False), uuid4()
            )

        mock_session.commit.assert_awaited_once()
        mv.assert_called_once_with(mock_updated)
        assert result == expected

    async def test_update_schedule_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.update_schedule(
                uuid4(), ScheduleUpdateDTO(status=False), uuid4()
            )

        mock_session.rollback.assert_awaited_once()

    async def test_delete_schedule_returns_none_when_not_found(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_schedule(uuid4(), uuid4())

        assert result is None
        mock_session.commit.assert_awaited_once()

    async def test_delete_schedule_returns_true_when_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_schedule(uuid4(), uuid4())

        assert result is True
        mock_session.commit.assert_awaited_once()

    async def test_delete_schedule_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.delete_schedule(uuid4(), uuid4())

        mock_session.rollback.assert_awaited_once()
