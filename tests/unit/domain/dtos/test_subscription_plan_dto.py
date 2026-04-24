from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.domain.dtos.subscription_plan import (
    SubscriptionPlanCreateDTO,
    SubscriptionPlanOutDTO,
    SubscriptionPlanUpdateDTO,
)


def test_create_dto_uses_per_month_rejects_zero():
    with pytest.raises(ValidationError):
        SubscriptionPlanCreateDTO(
            company_id=uuid4(),
            service_id=uuid4(),
            name='Plano',
            price=Decimal('10'),
            uses_per_month=0,
        )


def test_update_dto_uses_per_month_rejects_zero():
    with pytest.raises(ValidationError):
        SubscriptionPlanUpdateDTO(uses_per_month=0)


def test_update_dto_uses_per_month_accepts_positive():
    d = SubscriptionPlanUpdateDTO(uses_per_month=3)
    call_count = 3
    assert d.uses_per_month == call_count


def test_create_dto_accepts_unlimited_uses():
    d = SubscriptionPlanCreateDTO(
        company_id=uuid4(),
        service_id=uuid4(),
        name='Plano',
        price=Decimal('10'),
        uses_per_month=None,
    )
    assert d.uses_per_month is None


def test_out_dto_from_attributes():
    cid = uuid4()
    m = MagicMock()
    m.id = uuid4()
    m.company_id = cid
    m.service_id = uuid4()
    m.name = 'P'
    m.price = Decimal('1')
    m.uses_per_month = 2
    m.is_active = True
    m.created_at = datetime.now(timezone.utc)
    m.updated_at = m.created_at
    m.is_deleted = False
    o = SubscriptionPlanOutDTO.model_validate(m)
    assert o.name == 'P'
