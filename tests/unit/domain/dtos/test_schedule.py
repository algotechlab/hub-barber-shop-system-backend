from datetime import datetime, timezone
from uuid import uuid4

import pytest
from src.domain.dtos.schedule import ScheduleCreateDTO, ScheduleOutDTO

pytestmark = pytest.mark.unit


def _base_kwargs():
    return dict(
        user_id=uuid4(),
        service_id=uuid4(),
        product_id=uuid4(),
        employee_id=uuid4(),
        company_id=uuid4(),
        status=True,
        is_canceled=False,
    )


def test_schedule_create_dto_normalizes_timezone_aware_datetimes_to_naive_utc():
    dto = ScheduleCreateDTO(
        **_base_kwargs(),
        time_register=datetime(2026, 2, 14, 20, 6, 18, tzinfo=timezone.utc),
        time_start=datetime(2026, 2, 14, 21, 0, 0, tzinfo=timezone.utc),
        time_end=None,
    )

    assert dto.time_register.tzinfo is None
    assert dto.time_start.tzinfo is None
    assert dto.time_end is None
    assert dto.time_register == datetime(2026, 2, 14, 20, 6, 18)


def test_schedule_create_dto_keeps_naive_datetime_as_is():
    naive = datetime(2026, 2, 14, 20, 6, 18)
    dto = ScheduleCreateDTO(
        **_base_kwargs(),
        time_register=naive,
        time_start=None,
        time_end=None,
    )
    assert dto.time_register == naive
    assert dto.time_register.tzinfo is None


def test_schedule_out_dto_model_validate_accepts_orm_like_object_via_attributes():
    now = datetime(2026, 2, 14, 20, 6, 18)
    orm = type(
        'ScheduleOrm',
        (),
        dict(
            id=uuid4(),
            user_id=uuid4(),
            service_id=uuid4(),
            product_id=uuid4(),
            employee_id=uuid4(),
            company_id=uuid4(),
            time_register=now,
            time_start=None,
            time_end=None,
            status=True,
            is_canceled=False,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        ),
    )()

    dto = ScheduleOutDTO.model_validate(orm)
    assert dto.id == orm.id
    assert dto.company_id == orm.company_id
