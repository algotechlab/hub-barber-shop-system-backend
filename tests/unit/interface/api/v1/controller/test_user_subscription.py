import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.user_subscription import (
    UserSubscriptionOutDTO,
    UserSubscriptionWithPlanAndClientOutDTO,
    UserSubscriptionWithPlanOutDTO,
)
from src.interface.api.v1.controller.user_subscription import UserSubscriptionController
from src.interface.api.v1.schema.user_subscription import (
    ActivateUserSubscriptionAfterPaymentSchema,
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
            payment_at=None,
            payment_method=None,
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
            payment_at=None,
            payment_method=None,
            created_at=now,
            updated_at=now,
            is_deleted=False,
            plan_name='P',
            plan_price=Decimal('10'),
            plan_description=None,
            service_ids=[uuid.uuid4()],
            plan_product_lines=[],
            plan_uses_per_month=2,
        )
        use_case = AsyncMock()
        use_case.list_mine.return_value = [row]
        ctrl = UserSubscriptionController(use_case)
        p = PaginationParamsDTO()
        r = await ctrl.list_mine(p, company_id, user_id)
        assert len(r) == 1
        use_case.list_mine.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_pending(self):
        company_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        row = UserSubscriptionWithPlanAndClientOutDTO(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            subscription_plan_id=uuid.uuid4(),
            company_id=company_id,
            status='PENDING_PAYMENT',
            started_at=now,
            ended_at=None,
            external_subscription_id=None,
            payment_at=None,
            payment_method=None,
            created_at=now,
            updated_at=now,
            is_deleted=False,
            plan_name='P',
            plan_price=Decimal('10'),
            plan_description=None,
            service_ids=[uuid.uuid4()],
            plan_product_lines=[],
            plan_uses_per_month=2,
            client_name='João',
        )
        use_case = AsyncMock()
        use_case.list_pending_for_company.return_value = [row]
        ctrl = UserSubscriptionController(use_case)
        p = PaginationParamsDTO()
        r = await ctrl.list_pending(p, company_id, client_name='oã')
        assert len(r) == 1
        use_case.list_pending_for_company.assert_awaited_once_with(
            p, company_id, client_name='oã'
        )

    @pytest.mark.asyncio
    async def test_activate_after_payment(self):
        company_id, sid = uuid.uuid4(), uuid.uuid4()
        now = datetime.now(timezone.utc)
        out = UserSubscriptionOutDTO(
            id=sid,
            user_id=uuid.uuid4(),
            subscription_plan_id=uuid.uuid4(),
            company_id=company_id,
            status='ACTIVE',
            started_at=now,
            ended_at=None,
            external_subscription_id=None,
            payment_at=now,
            payment_method='MONEY',
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )
        use_case = AsyncMock()
        use_case.activate_after_payment.return_value = out
        ctrl = UserSubscriptionController(use_case)
        r = await ctrl.activate_after_payment(
            sid,
            company_id,
            ActivateUserSubscriptionAfterPaymentSchema(payment_method='MONEY'),
        )
        assert r.id == sid
        use_case.activate_after_payment.assert_awaited_once()
