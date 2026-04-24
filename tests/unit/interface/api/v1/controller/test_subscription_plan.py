import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.subscription_plan import SubscriptionPlanOutDTO
from src.interface.api.v1.controller.subscription_plan import SubscriptionPlanController
from src.interface.api.v1.schema.subscription_plan import (
    CreateSubscriptionPlanSchema,
    UpdateSubscriptionPlanSchema,
)


@pytest.mark.unit
class TestSubscriptionPlanController:
    @pytest.mark.asyncio
    async def test_list_plans(self):
        company_id = uuid.uuid4()
        use_case = AsyncMock()
        now = datetime.now(timezone.utc)
        use_case.list_plans.return_value = [
            SubscriptionPlanOutDTO(
                id=uuid.uuid4(),
                company_id=company_id,
                service_id=uuid.uuid4(),
                name='A',
                price=Decimal('1'),
                uses_per_month=None,
                is_active=True,
                created_at=now,
                updated_at=now,
                is_deleted=False,
            )
        ]
        ctrl = SubscriptionPlanController(use_case)
        p = PaginationParamsDTO()
        r = await ctrl.list_plans(p, company_id, active_only=True)
        assert len(r) == 1
        use_case.list_plans.assert_awaited_once_with(p, company_id, active_only=True)

    @pytest.mark.asyncio
    async def test_create_get_update_delete(self):
        company_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        out = SubscriptionPlanOutDTO(
            id=uuid.uuid4(),
            company_id=company_id,
            service_id=uuid.uuid4(),
            name='A',
            price=Decimal('1'),
            is_active=True,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )
        use_case = AsyncMock()
        use_case.create_plan.return_value = out
        use_case.get_plan.return_value = out
        use_case.update_plan.return_value = out
        use_case.delete_plan.return_value = None
        ctrl = SubscriptionPlanController(use_case)

        c = await ctrl.create_plan(
            CreateSubscriptionPlanSchema(
                service_id=out.service_id, name='A', price=Decimal('1')
            ),
            company_id=company_id,
        )
        assert c.id == out.id

        g = await ctrl.get_plan(out.id, company_id, active_only=False)
        assert g.name == 'A'

        u = await ctrl.update_plan(
            out.id,
            UpdateSubscriptionPlanSchema(name='B'),
            company_id=company_id,
        )
        assert u.id == out.id

        await ctrl.delete_plan(out.id, company_id=company_id)
        use_case.delete_plan.assert_awaited_once_with(out.id, company_id)
