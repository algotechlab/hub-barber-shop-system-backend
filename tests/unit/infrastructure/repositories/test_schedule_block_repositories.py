from datetime import date, time
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

    async def test_create_schedule_block_success(
        self, repo, mock_session, generate_schedule_block_create_dto
    ):
        now = MagicMock()
        mock_orm_block = MagicMock()
        mock_orm_block.id = uuid4()
        mock_orm_block.employee_id = generate_schedule_block_create_dto.employee_id
        mock_orm_block.company_id = generate_schedule_block_create_dto.company_id
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
        assert (
            model_payload['start_date'] == generate_schedule_block_create_dto.start_date
        )
        assert model_payload['end_date'] == generate_schedule_block_create_dto.end_date
        assert (
            model_payload['start_time'] == generate_schedule_block_create_dto.start_time
        )
        assert model_payload['end_time'] == generate_schedule_block_create_dto.end_time
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

    async def test_list_schedule_blocks_success(self, repo, mock_session):
        employee_id = uuid4()
        mock_orm_block = MagicMock()
        mock_orm_block.id = uuid4()
        mock_orm_block.start_date = date(2026, 3, 1)
        mock_orm_block.end_date = date(2026, 3, 2)
        mock_orm_block.start_time = time(9, 0)
        mock_orm_block.end_time = time(17, 0)
        mock_orm_block.is_block = True
        mock_orm_block.created_at = MagicMock()
        mock_orm_block.updated_at = MagicMock()

        mock_result = MagicMock()
        mock_result.all.return_value = [(mock_orm_block, employee_id, 'John Doe')]
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.list_schedule_blocks(uuid4())

        assert len(result) == 1
        assert result[0].id == mock_orm_block.id
        assert result[0].employee_id == employee_id
        assert result[0].employee_name == 'John Doe'
        assert result[0].start_date == mock_orm_block.start_date
        assert result[0].end_date == mock_orm_block.end_date
        assert result[0].start_time == mock_orm_block.start_time
        assert result[0].end_time == mock_orm_block.end_time
        assert result[0].is_block is True

    async def test_list_schedule_blocks_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.list_schedule_blocks(uuid4())

        mock_session.rollback.assert_awaited_once()

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
