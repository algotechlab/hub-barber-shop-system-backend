from datetime import date, time
from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.interface.api.v1.schema.schedule_block import (
    CreateScheduleBlockSchema,
    UpdateScheduleBlockSchema,
)

pytestmark = pytest.mark.unit


def test_create_schedule_block_schema_accepts_valid_date_range():
    schema = CreateScheduleBlockSchema(
        employee_id=uuid4(),
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 10),
        start_time=time(9, 0),
        end_time=time(18, 0),
    )

    assert schema.start_date == date(2026, 5, 1)
    assert schema.end_date == date(2026, 5, 10)


def test_update_schedule_block_schema_accepts_valid_date_range_when_both_set():
    schema = UpdateScheduleBlockSchema(
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 10),
    )

    assert schema.start_date == date(2026, 5, 1)
    assert schema.end_date == date(2026, 5, 10)


def test_update_schedule_block_schema_skips_date_range_check_when_only_one_date():
    schema = UpdateScheduleBlockSchema(start_date=date(2026, 5, 1))

    assert schema.start_date == date(2026, 5, 1)
    assert schema.end_date is None


def test_create_schedule_block_schema_rejects_end_date_before_start_date():
    with pytest.raises(ValidationError) as exc_info:
        CreateScheduleBlockSchema(
            employee_id=uuid4(),
            start_date=date(2026, 5, 10),
            end_date=date(2026, 5, 1),
            start_time=time(9, 0),
            end_time=time(18, 0),
        )

    assert 'end_date must be greater than or equal to start_date' in str(exc_info.value)


def test_update_schedule_block_date_when_both_set():
    with pytest.raises(ValidationError) as exc_info:
        UpdateScheduleBlockSchema(
            start_date=date(2026, 5, 10),
            end_date=date(2026, 5, 1),
        )

    assert 'end_date must be greater than or equal to start_date' in str(exc_info.value)
