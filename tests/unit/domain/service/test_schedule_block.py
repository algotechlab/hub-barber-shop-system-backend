from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.schedule_block import ScheduleBlockUpdateDTO
from src.domain.service.schedule_block import ScheduleBlockService


@pytest.mark.unit
class TestScheduleBlockService:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository):
        return ScheduleBlockService(schedule_block_repository=mock_repository)

    async def test_create_schedule_block_delegates_to_repository(
        self,
        service,
        mock_repository,
        generate_schedule_block_create_dto,
        generate_schedule_block_out_dto,
    ):
        mock_repository.create_schedule_block.return_value = (
            generate_schedule_block_out_dto
        )

        result = await service.create_schedule_block(generate_schedule_block_create_dto)

        mock_repository.create_schedule_block.assert_awaited_once_with(
            generate_schedule_block_create_dto
        )
        assert result == generate_schedule_block_out_dto

    async def test_get_schedule_block_delegates_to_repository(
        self, service, mock_repository, generate_schedule_block_out_dto
    ):
        block_id = uuid4()
        mock_repository.get_schedule_block.return_value = (
            generate_schedule_block_out_dto
        )

        result = await service.get_schedule_block(block_id)

        mock_repository.get_schedule_block.assert_awaited_once_with(block_id)
        assert result == generate_schedule_block_out_dto

    async def test_list_schedule_blocks_delegates_to_repository(
        self, service, mock_repository, generate_schedule_block_out_list_dto
    ):
        company_id = uuid4()
        mock_repository.list_schedule_blocks.return_value = (
            generate_schedule_block_out_list_dto
        )

        result = await service.list_schedule_blocks(company_id)

        mock_repository.list_schedule_blocks.assert_awaited_once_with(company_id)
        assert result == generate_schedule_block_out_list_dto

    async def test_update_schedule_block_delegates_to_repository(
        self, service, mock_repository, generate_schedule_block_out_dto
    ):
        block_id = uuid4()
        update_dto = ScheduleBlockUpdateDTO(is_block=True)
        mock_repository.update_schedule_block.return_value = (
            generate_schedule_block_out_dto
        )

        result = await service.update_schedule_block(block_id, update_dto)

        mock_repository.update_schedule_block.assert_awaited_once_with(
            block_id, update_dto
        )
        assert result == generate_schedule_block_out_dto

    async def test_delete_schedule_block_delegates_to_repository(
        self, service, mock_repository
    ):
        block_id = uuid4()
        mock_repository.delete_schedule_block.return_value = True

        result = await service.delete_schedule_block(block_id)

        mock_repository.delete_schedule_block.assert_awaited_once_with(block_id)
        assert result is True
