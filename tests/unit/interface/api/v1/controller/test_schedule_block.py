from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.schedule_block import (
    ScheduleBlockCreateDTO,
    ScheduleBlockUpdateDTO,
)
from src.interface.api.v1.controller.schedule_block import ScheduleBlockController
from src.interface.api.v1.schema.schedule_block import (
    CreateScheduleBlockSchema,
    ScheduleBlockOutListSchema,
    ScheduleBlockOutSchema,
    UpdateScheduleBlockSchema,
)


@pytest.mark.unit
class TestScheduleBlockController:
    @pytest.fixture
    def mock_use_case(self):
        return AsyncMock()

    @pytest.fixture
    def controller(self, mock_use_case):
        return ScheduleBlockController(schedule_block_use_case=mock_use_case)

    async def test_create_schedule_block_converts_schema_to_dto(
        self, controller, mock_use_case, generate_schedule_block_out_dto
    ):
        company_id = uuid4()
        payload = CreateScheduleBlockSchema(
            employee_id=uuid4(),
            start_date=generate_schedule_block_out_dto.start_date,
            end_date=generate_schedule_block_out_dto.end_date,
            start_time=generate_schedule_block_out_dto.start_time,
            end_time=generate_schedule_block_out_dto.end_time,
        )
        mock_use_case.create_schedule_block.return_value = (
            generate_schedule_block_out_dto
        )

        result = await controller.create_schedule_block(payload, company_id)

        mock_use_case.create_schedule_block.assert_awaited_once()
        sent_dto = mock_use_case.create_schedule_block.call_args[0][0]
        assert isinstance(sent_dto, ScheduleBlockCreateDTO)
        assert sent_dto.employee_id == payload.employee_id
        assert sent_dto.company_id == company_id
        assert isinstance(result, ScheduleBlockOutSchema)
        assert result.id == generate_schedule_block_out_dto.id

    async def test_get_schedule_block_returns_schema(
        self, controller, mock_use_case, generate_schedule_block_out_dto
    ):
        block_id = uuid4()
        mock_use_case.get_schedule_block.return_value = generate_schedule_block_out_dto

        result = await controller.get_schedule_block(block_id)

        mock_use_case.get_schedule_block.assert_awaited_once_with(block_id)
        assert isinstance(result, ScheduleBlockOutSchema)
        assert result.id == generate_schedule_block_out_dto.id

    async def test_list_schedule_blocks_returns_schema_list(
        self, controller, mock_use_case, generate_schedule_block_out_list_dto
    ):
        mock_use_case.list_schedule_blocks.return_value = (
            generate_schedule_block_out_list_dto
        )
        company_id = uuid4()
        result = await controller.list_schedule_blocks(company_id)
        mock_use_case.list_schedule_blocks.assert_awaited_once_with(company_id)
        assert isinstance(result, list)
        assert all(
            isinstance(schedule_block, ScheduleBlockOutListSchema)
            for schedule_block in result
        )
        assert [item.model_dump() for item in result] == [
            item.model_dump() for item in generate_schedule_block_out_list_dto
        ]

    async def test_update_schedule_block_converts_schema_to_dto(
        self, controller, mock_use_case, generate_schedule_block_out_dto
    ):
        block_id = uuid4()
        payload = UpdateScheduleBlockSchema()
        mock_use_case.update_schedule_block.return_value = (
            generate_schedule_block_out_dto
        )

        await controller.update_schedule_block(block_id, payload)

        mock_use_case.update_schedule_block.assert_awaited_once()
        call_args = mock_use_case.update_schedule_block.call_args[0]
        assert call_args[0] == block_id
        assert isinstance(call_args[1], ScheduleBlockUpdateDTO)

    async def test_delete_schedule_block_delegates_to_use_case(
        self, controller, mock_use_case
    ):
        block_id = uuid4()
        mock_use_case.delete_schedule_block.return_value = True

        result = await controller.delete_schedule_block(block_id)

        mock_use_case.delete_schedule_block.assert_awaited_once_with(block_id)
        assert result is True
