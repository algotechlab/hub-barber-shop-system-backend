from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

import pytest
from src.domain.dtos.schedule_block import (
    ScheduleBlockCreateDTO,
    ScheduleBlockOutDTO,
    ScheduleBlockOutListDTO,
    ScheduleBlockUpdateDTO,
)
from src.domain.repositories.schedule_block import ScheduleBlockRepository


@pytest.mark.unit
class TestScheduleBlockRepositoryContract:
    def test_schedule_block_repository_exposes_contract_methods(self):
        assert hasattr(ScheduleBlockRepository, 'create_schedule_block')
        assert hasattr(ScheduleBlockRepository, 'get_schedule_block')
        assert hasattr(ScheduleBlockRepository, 'list_schedule_blocks')
        assert hasattr(ScheduleBlockRepository, 'update_schedule_block')
        assert hasattr(ScheduleBlockRepository, 'delete_schedule_block')

        assert getattr(
            ScheduleBlockRepository.create_schedule_block, '__isabstractmethod__', False
        )
        assert getattr(
            ScheduleBlockRepository.get_schedule_block, '__isabstractmethod__', False
        )
        assert getattr(
            ScheduleBlockRepository.update_schedule_block, '__isabstractmethod__', False
        )
        assert getattr(
            ScheduleBlockRepository.delete_schedule_block, '__isabstractmethod__', False
        )

    async def test_can_implement_concrete_repository(self):
        now = datetime.now(timezone.utc)
        block_id = uuid4()
        employee_id = uuid4()
        company_id = uuid4()
        create_dto = ScheduleBlockCreateDTO(
            employee_id=employee_id,
            company_id=company_id,
            start_time=now,
            end_time=now,
        )
        out = ScheduleBlockOutDTO(
            id=block_id,
            employee_id=employee_id,
            company_id=company_id,
            start_time=now,
            end_time=now,
            is_block=False,
            created_at=now,
            updated_at=now,
        )

        class ConcreteScheduleBlockRepository(ScheduleBlockRepository):
            async def create_schedule_block(
                self, schedule_block: ScheduleBlockCreateDTO
            ) -> ScheduleBlockOutDTO:
                return out

            async def get_schedule_block(self, id: UUID) -> ScheduleBlockOutDTO | None:
                return out if id == block_id else None

            async def list_schedule_blocks(
                self, company_id: UUID
            ) -> List[ScheduleBlockOutListDTO]:
                return [out]

            async def update_schedule_block(
                self, id: UUID, schedule_block: ScheduleBlockUpdateDTO
            ) -> ScheduleBlockOutDTO | None:
                return out if id == block_id else None

            async def delete_schedule_block(self, id: UUID) -> bool:
                return id == block_id

        repository = ConcreteScheduleBlockRepository()

        created = await repository.create_schedule_block(create_dto)
        assert created == out

        found = await repository.get_schedule_block(block_id)
        assert found == out

        updated = await repository.update_schedule_block(
            block_id, ScheduleBlockUpdateDTO(is_block=True)
        )
        assert updated == out

        deleted = await repository.delete_schedule_block(block_id)
        assert deleted is True
