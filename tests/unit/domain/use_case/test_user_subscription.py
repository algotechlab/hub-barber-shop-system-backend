from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.user_subscription import UserSubscriptionOutDTO
from src.domain.exceptions.subscription import (
    SubscriptionPlanNotFoundException,
    UserSubscriptionActiveExistsException,
)
from src.domain.use_case.user_subscription import UserSubscriptionUseCase

pytestmark = pytest.mark.unit


def _us_out(company_id, user_id, plan_id):
    now = datetime.now(timezone.utc)
    return UserSubscriptionOutDTO(
        id=uuid4(),
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


@pytest.mark.asyncio
async def test_create_for_user_plan_not_found():
    us = AsyncMock()
    plan = AsyncMock()
    plan.get_plan.return_value = None
    uc = UserSubscriptionUseCase(us, plan)
    with pytest.raises(SubscriptionPlanNotFoundException):
        await uc.create_for_user(
            user_id=uuid4(),
            company_id=uuid4(),
            subscription_plan_id=uuid4(),
        )
    us.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_for_user_active_exists():
    us = AsyncMock()
    us.has_active_for_plan.return_value = True
    plan = AsyncMock()
    plan.get_plan.return_value = AsyncMock()
    uc = UserSubscriptionUseCase(us, plan)
    with pytest.raises(UserSubscriptionActiveExistsException):
        await uc.create_for_user(
            user_id=uuid4(),
            company_id=uuid4(),
            subscription_plan_id=uuid4(),
        )
    us.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_for_user_success():
    us = AsyncMock()
    us.has_active_for_plan.return_value = False
    plan = AsyncMock()
    cid, uid, pid = uuid4(), uuid4(), uuid4()
    plan.get_plan.return_value = AsyncMock()
    expected = _us_out(cid, uid, pid)
    us.create.return_value = expected
    uc = UserSubscriptionUseCase(us, plan)
    r = await uc.create_for_user(user_id=uid, company_id=cid, subscription_plan_id=pid)
    assert r == expected
    plan.get_plan.assert_awaited_once_with(pid, cid, active_only=True)
    us.create.assert_awaited_once()
    call = us.create.call_args[0][0]
    assert call.user_id == uid
    assert call.subscription_plan_id == pid


@pytest.mark.asyncio
async def test_list_mine_delegates():
    us = AsyncMock()
    us.list_by_user.return_value = []
    plan = AsyncMock()
    uc = UserSubscriptionUseCase(us, plan)
    p = PaginationParamsDTO()
    cid, uid = uuid4(), uuid4()
    r = await uc.list_mine(p, cid, uid)
    assert r == []
    us.list_by_user.assert_awaited_once_with(p, cid, uid)
