from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.schedule_block import ScheduleBlockUpdateDTO
from src.domain.exceptions.schedule_block import ScheduleBlockNotFoundException
from src.domain.use_case.schedule_block import ScheduleBlockUseCase


@pytest.mark.unit
class TestScheduleBlockUseCase:
    @pytest.fixture
    def mock_service(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_service):
        return ScheduleBlockUseCase(schedule_block_service=mock_service)

    async def test_create_schedule_block_delegates_to_service(
        self,
        use_case,
        mock_service,
        generate_schedule_block_create_dto,
        generate_schedule_block_out_dto,
    ):
        mock_service.create_schedule_block.return_value = (
            generate_schedule_block_out_dto
        )

        result = await use_case.create_schedule_block(
            generate_schedule_block_create_dto
        )

        mock_service.create_schedule_block.assert_awaited_once_with(
            generate_schedule_block_create_dto
        )
        assert result == generate_schedule_block_out_dto

    async def test_get_schedule_block_raises_when_not_found(
        self, use_case, mock_service
    ):
        mock_service.get_schedule_block.return_value = None

        with pytest.raises(ScheduleBlockNotFoundException):
            await use_case.get_schedule_block(uuid4())

    async def test_get_schedule_block_returns_when_found(
        self, use_case, mock_service, generate_schedule_block_out_dto
    ):
        block_id = uuid4()
        mock_service.get_schedule_block.return_value = generate_schedule_block_out_dto

        result = await use_case.get_schedule_block(block_id)

        mock_service.get_schedule_block.assert_awaited_once_with(block_id)
        assert result == generate_schedule_block_out_dto

    async def test_update_schedule_block_delegates_to_service(
        self, use_case, mock_service, generate_schedule_block_out_dto
    ):
        block_id = uuid4()
        update_dto = ScheduleBlockUpdateDTO(is_block=True)
        mock_service.update_schedule_block.return_value = (
            generate_schedule_block_out_dto
        )

        result = await use_case.update_schedule_block(block_id, update_dto)

        mock_service.update_schedule_block.assert_awaited_once_with(
            block_id, update_dto
        )
        assert result == generate_schedule_block_out_dto

    async def test_delete_schedule_block_raises_when_not_deleted(
        self, use_case, mock_service
    ):
        mock_service.delete_schedule_block.return_value = False

        with pytest.raises(ScheduleBlockNotFoundException):
            await use_case.delete_schedule_block(uuid4())

    async def test_delete_schedule_block_returns_true_when_deleted(
        self, use_case, mock_service
    ):
        block_id = uuid4()
        mock_service.delete_schedule_block.return_value = True

        result = await use_case.delete_schedule_block(block_id)

        mock_service.delete_schedule_block.assert_awaited_once_with(block_id)
        assert result is True
