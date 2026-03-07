from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.schedule_block import ScheduleBlockOutDTO, ScheduleBlockUpdateDTO
from src.infrastructure.repositories.schedule_block_postgres import (
    ScheduleBlockRepositoryPostgres,
)


@pytest.mark.unit
class TestScheduleBlockRepositoryPostgres:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session):
        return ScheduleBlockRepositoryPostgres(session=mock_session)

    def test_to_db_naive_utc_keeps_naive_datetime(self, repo):
        naive = datetime(2026, 3, 7, 16, 3, 18)

        result = repo._to_db_naive_utc(naive)

        assert result == naive
        assert result.tzinfo is None

    async def test_create_schedule_block_success(
        self, repo, mock_session, generate_schedule_block_create_dto
    ):
        now = datetime.now(timezone.utc)
        mock_orm_block = MagicMock()
        mock_orm_block.id = uuid4()
        mock_orm_block.employee_id = generate_schedule_block_create_dto.employee_id
        mock_orm_block.company_id = generate_schedule_block_create_dto.company_id
        mock_orm_block.start_time = datetime.now()
        mock_orm_block.end_time = datetime.now()
        mock_orm_block.is_block = False
        mock_orm_block.created_at = now
        mock_orm_block.updated_at = now
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        expected_dto = MagicMock(spec=ScheduleBlockOutDTO)

        with (
            patch(
                'src.infrastructure.repositories.schedule_block_postgres.ScheduleBlock',
                return_value=mock_orm_block,
            ) as mock_model,
            patch.object(
                ScheduleBlockOutDTO, 'model_validate', return_value=expected_dto
            ) as mock_validate,
        ):
            result = await repo.create_schedule_block(
                generate_schedule_block_create_dto
            )

        mock_session.add.assert_called_once_with(mock_orm_block)
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(mock_orm_block)
        mock_model.assert_called_once()
        model_payload = mock_model.call_args.kwargs
        assert model_payload['start_time'].tzinfo is None
        assert model_payload['end_time'].tzinfo is None
        mock_validate.assert_called_once_with(mock_orm_block)
        assert result == expected_dto

    async def test_create_schedule_block_rollback_on_error(
        self, repo, mock_session, generate_schedule_block_create_dto
    ):
        mock_session.add = MagicMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.create_schedule_block(generate_schedule_block_create_dto)

        mock_session.rollback.assert_awaited_once()

    async def test_get_schedule_block_returns_none_when_not_found(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_schedule_block(uuid4())

        assert result is None

    async def test_get_schedule_block_success(
        self, repo, mock_session, generate_schedule_block_out_dto
    ):
        mock_orm_block = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_orm_block
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch.object(
            ScheduleBlockOutDTO,
            'model_validate',
            return_value=generate_schedule_block_out_dto,
        ) as mock_validate:
            result = await repo.get_schedule_block(uuid4())

        mock_validate.assert_called_once_with(mock_orm_block)
        assert result == generate_schedule_block_out_dto

    async def test_get_schedule_block_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_schedule_block(uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_update_schedule_block_returns_none_when_not_found(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.update_schedule_block(uuid4(), ScheduleBlockUpdateDTO())

        assert result is None

    async def test_update_schedule_block_success(
        self, repo, mock_session, generate_schedule_block_out_dto
    ):
        mock_updated_orm = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_updated_orm
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        with patch.object(
            ScheduleBlockOutDTO,
            'model_validate',
            return_value=generate_schedule_block_out_dto,
        ):
            result = await repo.update_schedule_block(
                uuid4(), ScheduleBlockUpdateDTO(is_block=True)
            )

        mock_session.commit.assert_awaited_once()
        assert result == generate_schedule_block_out_dto

    async def test_update_schedule_block_normalizes_start_and_end_time(
        self, repo, mock_session, generate_schedule_block_out_dto
    ):
        mock_updated_orm = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_updated_orm
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        aware_start = datetime(2026, 3, 7, 16, 3, 18, tzinfo=timezone.utc)
        aware_end = datetime(2026, 3, 7, 17, 3, 18, tzinfo=timezone.utc)

        with (
            patch.object(
                ScheduleBlockOutDTO,
                'model_validate',
                return_value=generate_schedule_block_out_dto,
            ),
            patch.object(
                repo,
                '_to_db_naive_utc',
                wraps=repo._to_db_naive_utc,
            ) as normalize,
        ):
            await repo.update_schedule_block(
                uuid4(),
                ScheduleBlockUpdateDTO(
                    start_time=aware_start,
                    end_time=aware_end,
                ),
            )
        arrange_call_count = 2
        assert normalize.call_count == arrange_call_count

    async def test_update_schedule_block_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.update_schedule_block(uuid4(), ScheduleBlockUpdateDTO())

        mock_session.rollback.assert_awaited_once()

    async def test_delete_schedule_block_returns_true_when_found(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_schedule_block(uuid4())

        assert result is True
        mock_session.commit.assert_awaited_once()

    async def test_delete_schedule_block_returns_false_when_not_found(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_schedule_block(uuid4())

        assert result is False
        mock_session.commit.assert_awaited_once()

    async def test_delete_schedule_block_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.delete_schedule_block(uuid4())

        mock_session.rollback.assert_awaited_once()
