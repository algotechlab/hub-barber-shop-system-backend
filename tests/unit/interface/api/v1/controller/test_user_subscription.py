import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.user_subscription import (
    UserSubscriptionOutDTO,
    UserSubscriptionWithPlanOutDTO,
)
from src.interface.api.v1.controller.user_subscription import UserSubscriptionController
from src.interface.api.v1.schema.user_subscription import (
    CreateUserSubscriptionSchema,
)


@pytest.mark.unit
class TestUserSubscriptionController:
    @pytest.mark.asyncio
    async def test_create(self):
        company_id, user_id, plan_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        now = datetime.now(timezone.utc)
        out = UserSubscriptionOutDTO(
            id=uuid.uuid4(),
            user_id=user_id,
            subscription_plan_id=plan_id,
            company_id=company_id,
            status='ACTIVE',
            started_at=now,
            ended_at=None,
            external_subscription_id=None,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )
        use_case = AsyncMock()
        use_case.create_for_user.return_value = out
        ctrl = UserSubscriptionController(use_case)
        r = await ctrl.create(
            CreateUserSubscriptionSchema(subscription_plan_id=plan_id),
            company_id=company_id,
            user_id=user_id,
        )
        assert r.id == out.id
        use_case.create_for_user.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_mine(self):
        company_id, user_id = uuid.uuid4(), uuid.uuid4()
        now = datetime.now(timezone.utc)
        row = UserSubscriptionWithPlanOutDTO(
            id=uuid.uuid4(),
            user_id=user_id,
            subscription_plan_id=uuid.uuid4(),
            company_id=company_id,
            status='ACTIVE',
            started_at=now,
            ended_at=None,
            external_subscription_id=None,
            created_at=now,
            updated_at=now,
            is_deleted=False,
            plan_name='P',
            plan_price=Decimal('10'),
            service_id=uuid.uuid4(),
            plan_uses_per_month=2,
        )
        use_case = AsyncMock()
        use_case.list_mine.return_value = [row]
        ctrl = UserSubscriptionController(use_case)
        p = PaginationParamsDTO()
        r = await ctrl.list_mine(p, company_id, user_id)
        assert len(r) == 1
        use_case.list_mine.assert_awaited_once()
