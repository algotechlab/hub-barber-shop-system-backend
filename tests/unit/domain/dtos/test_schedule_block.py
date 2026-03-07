from datetime import datetime, timezone
from uuid import uuid4

import pytest
from src.domain.dtos.schedule_block import (
    ScheduleBlockCreateDTO,
    ScheduleBlockOutDTO,
    ScheduleBlockUpdateDTO,
)

pytestmark = pytest.mark.unit


def test_schedule_block_create_dto_accepts_required_fields():
    dto = ScheduleBlockCreateDTO(
        employee_id=uuid4(),
        company_id=uuid4(),
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
    )

    assert dto.employee_id is not None
    assert dto.company_id is not None


def test_schedule_block_out_dto_model_validate_accepts_orm_like_object():
    now = datetime.now(timezone.utc)
    orm = type(
        'ScheduleBlockOrm',
        (),
        dict(
            id=uuid4(),
            employee_id=uuid4(),
            company_id=uuid4(),
            start_time=now,
            end_time=now,
            is_block=True,
            created_at=now,
            updated_at=now,
        ),
    )()

    dto = ScheduleBlockOutDTO.model_validate(orm)

    assert dto.id == orm.id
    assert dto.company_id == orm.company_id
    assert dto.is_block is True


def test_schedule_block_update_dto_excludes_none():
    dto = ScheduleBlockUpdateDTO(is_block=True)

    dumped = dto.model_dump(exclude_none=True)

    assert dumped == {'is_block': True}
