from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.domain.dtos.subscription_plan import (
    SubscriptionPlanCreateDTO,
    SubscriptionPlanOutDTO,
    SubscriptionPlanProductLineOutDTO,
    SubscriptionPlanUpdateDTO,
)


def test_create_dto_uses_per_month_rejects_zero():
    with pytest.raises(ValidationError):
        SubscriptionPlanCreateDTO(
            company_id=uuid4(),
            service_ids=[uuid4()],
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
        service_ids=[uuid4()],
        name='Plano',
        price=Decimal('10'),
        uses_per_month=None,
    )
    assert d.uses_per_month is None


def test_create_dto_rejects_product_line_quantity_below_one():
    with pytest.raises(ValidationError):
        SubscriptionPlanCreateDTO(
            company_id=uuid4(),
            service_ids=[uuid4()],
            name='Plano',
            price=Decimal('10'),
            product_lines=[
                SubscriptionPlanProductLineOutDTO(product_id=uuid4(), quantity=0)
            ],
        )


def test_create_dto_rejects_duplicate_product_id_in_lines():
    pid = uuid4()
    with pytest.raises(ValidationError):
        SubscriptionPlanCreateDTO(
            company_id=uuid4(),
            service_ids=[uuid4()],
            name='Plano',
            price=Decimal('10'),
            product_lines=[
                SubscriptionPlanProductLineOutDTO(product_id=pid, quantity=1),
                SubscriptionPlanProductLineOutDTO(product_id=pid, quantity=2),
            ],
        )


def test_create_dto_rejects_duplicate_service_ids():
    sid = uuid4()
    with pytest.raises(ValidationError):
        SubscriptionPlanCreateDTO(
            company_id=uuid4(),
            service_ids=[sid, sid],
            name='Plano',
            price=Decimal('10'),
        )


def test_update_dto_rejects_empty_service_ids_when_set():
    with pytest.raises(ValidationError):
        SubscriptionPlanUpdateDTO(service_ids=[])


def test_update_dto_product_lines_none_skips_qty_validation():
    d = SubscriptionPlanUpdateDTO(product_lines=None)
    assert d.product_lines is None


def test_update_dto_rejects_product_line_quantity_below_one():
    with pytest.raises(ValidationError):
        SubscriptionPlanUpdateDTO(
            product_lines=[
                SubscriptionPlanProductLineOutDTO(product_id=uuid4(), quantity=0)
            ],
        )


def test_update_dto_rejects_duplicate_product_id_in_lines():
    pid = uuid4()
    with pytest.raises(ValidationError):
        SubscriptionPlanUpdateDTO(
            product_lines=[
                SubscriptionPlanProductLineOutDTO(product_id=pid, quantity=1),
                SubscriptionPlanProductLineOutDTO(product_id=pid, quantity=1),
            ],
        )


def test_update_dto_rejects_duplicate_service_ids():
    sid = uuid4()
    with pytest.raises(ValidationError):
        SubscriptionPlanUpdateDTO(service_ids=[sid, sid])


def test_out_dto_constructs():
    cid = uuid4()
    o = SubscriptionPlanOutDTO(
        id=uuid4(),
        company_id=cid,
        name='P',
        description='d',
        service_ids=[uuid4()],
        product_lines=[
            SubscriptionPlanProductLineOutDTO(product_id=uuid4(), quantity=1)
        ],
        price=Decimal('1'),
        uses_per_month=2,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_deleted=False,
    )
    assert o.name == 'P'
