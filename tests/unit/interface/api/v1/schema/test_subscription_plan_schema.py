from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.interface.api.v1.schema.subscription_plan import (
    CreateSubscriptionPlanSchema,
    UpdateSubscriptionPlanSchema,
)


def test_create_schema_uses_rejects_zero():
    with pytest.raises(ValidationError):
        CreateSubscriptionPlanSchema(
            service_id=uuid4(),
            name='A',
            price=Decimal('1'),
            uses_per_month=0,
        )


def test_update_schema_uses_rejects_zero():
    with pytest.raises(ValidationError):
        UpdateSubscriptionPlanSchema(uses_per_month=0)
