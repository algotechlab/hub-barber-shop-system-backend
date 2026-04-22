from datetime import date, datetime, time, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError
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
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 5),
        start_time=time(9, 0),
        end_time=time(18, 0),
    )

    assert dto.employee_id is not None
    assert dto.company_id is not None
    assert dto.start_date == date(2026, 3, 1)
    assert dto.end_date == date(2026, 3, 5)


def test_schedule_block_create_dto_rejects_inverted_date_range():
    with pytest.raises(ValidationError):
        ScheduleBlockCreateDTO(
            employee_id=uuid4(),
            company_id=uuid4(),
            start_date=date(2026, 3, 10),
            end_date=date(2026, 3, 1),
            start_time=time(9, 0),
            end_time=time(18, 0),
        )


def test_schedule_block_out_dto_model_validate_accepts_orm_like_object():
    now = datetime.now(timezone.utc)
    orm = type(
        'ScheduleBlockOrm',
        (),
        dict(
            id=uuid4(),
            employee_id=uuid4(),
            company_id=uuid4(),
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 2),
            start_time=time(8, 0),
            end_time=time(12, 0),
            is_block=True,
            created_at=now,
            updated_at=now,
        ),
    )()

    dto = ScheduleBlockOutDTO.model_validate(orm)

    assert dto.id == orm.id
    assert dto.company_id == orm.company_id
    assert dto.is_block is True
    assert dto.start_date == orm.start_date


def test_schedule_block_update_dto_excludes_none():
    dto = ScheduleBlockUpdateDTO(is_block=True)

    dumped = dto.model_dump(exclude_none=True)

    assert dumped == {'is_block': True}


def test_schedule_block_update_dto_rejects_inverted_date_range_when_both_set():
    with pytest.raises(ValidationError):
        ScheduleBlockUpdateDTO(
            start_date=date(2026, 5, 10),
            end_date=date(2026, 5, 1),
        )
