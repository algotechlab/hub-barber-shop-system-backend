from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.user_subscription import UserSubscriptionCreateDTO
from src.domain.service.user_subscription import UserSubscriptionService

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_user_subscription_service_delegates():
    repo = AsyncMock()
    service = UserSubscriptionService(repo)
    p = PaginationParamsDTO()
    uid, cid, plan_id = uuid4(), uuid4(), uuid4()

    dto = UserSubscriptionCreateDTO(
        user_id=uid, company_id=cid, subscription_plan_id=plan_id
    )
    repo.create.return_value = AsyncMock()
    await service.create(dto)
    repo.create.assert_awaited_once_with(dto)

    repo.list_by_user.return_value = []
    assert await service.list_by_user(p, cid, uid) == []

    repo.has_active_for_plan.return_value = False
    assert await service.has_active_for_plan(uid, plan_id, cid) is False
