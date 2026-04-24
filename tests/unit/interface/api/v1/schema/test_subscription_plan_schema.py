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
    with pytest.raises(ValidationError):
        UpdateSubscriptionPlanSchema(
            product_lines=[
                SubscriptionPlanProductLineSchema(product_id=pid, quantity=1),
                SubscriptionPlanProductLineSchema(product_id=pid, quantity=1),
            ],
        )


def test_update_schema_rejects_duplicate_service_ids():
    sid = uuid4()
    with pytest.raises(ValidationError):
        UpdateSubscriptionPlanSchema(service_ids=[sid, sid])
