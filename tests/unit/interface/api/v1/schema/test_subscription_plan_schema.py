from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.interface.api.v1.schema.subscription_plan import (
    CreateSubscriptionPlanSchema,
    SubscriptionPlanProductLineSchema,
    UpdateSubscriptionPlanSchema,
)


def test_create_schema_uses_rejects_zero():
    with pytest.raises(ValidationError):
        CreateSubscriptionPlanSchema(
            service_ids=[uuid4()],
            name='A',
            price=Decimal('1'),
            uses_per_month=0,
        )


def test_update_schema_uses_rejects_zero():
    with pytest.raises(ValidationError):
        UpdateSubscriptionPlanSchema(uses_per_month=0)


def test_create_schema_rejects_duplicate_product_lines():
    pid = uuid4()
    with pytest.raises(ValidationError):
        CreateSubscriptionPlanSchema(
            service_ids=[uuid4()],
            name='A',
            price=Decimal('1'),
            product_lines=[
                SubscriptionPlanProductLineSchema(product_id=pid, quantity=1),
                SubscriptionPlanProductLineSchema(product_id=pid, quantity=2),
            ],
        )


def test_create_schema_rejects_duplicate_service_ids():
    sid = uuid4()
    with pytest.raises(ValidationError):
        CreateSubscriptionPlanSchema(
            service_ids=[sid, sid],
            name='A',
            price=Decimal('1'),
        )


def test_update_schema_rejects_duplicate_product_lines():
    pid = uuid4()
    with pytest.raises(ValidationError) as exc_info:
        UpdateSubscriptionPlanSchema(
            product_lines=[
                SubscriptionPlanProductLineSchema(product_id=pid, quantity=1),
                SubscriptionPlanProductLineSchema(product_id=pid, quantity=1),
            ],
        )
    assert 'product_lines não pode repetir o mesmo product_id' in str(exc_info.value)


def test_update_schema_product_lines_none_does_not_run_uniqueness_check():
    s = UpdateSubscriptionPlanSchema(name='Só nome', product_lines=None)
    assert s.product_lines is None


def test_update_schema_accepts_empty_product_lines():
    s = UpdateSubscriptionPlanSchema(product_lines=[])
    assert s.product_lines == []


def test_update_schema_accepts_distinct_product_lines():
    a, b = uuid4(), uuid4()
    s = UpdateSubscriptionPlanSchema(
        product_lines=[
            SubscriptionPlanProductLineSchema(product_id=a, quantity=1),
            SubscriptionPlanProductLineSchema(product_id=b, quantity=2),
        ],
    )
    assert [p.product_id for p in s.product_lines] == [a, b]


def test_update_schema_rejects_duplicate_service_ids():
    sid = uuid4()
    with pytest.raises(ValidationError):
        UpdateSubscriptionPlanSchema(service_ids=[sid, sid])
