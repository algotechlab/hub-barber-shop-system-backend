from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.subscription_plan import (
    SubscriptionPlanCreateDTO,
    SubscriptionPlanUpdateDTO,
)
from src.domain.service.subscription_plan import SubscriptionPlanService

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_service_create_delegates():
    repo = AsyncMock()
    service = SubscriptionPlanService(repo)
    dto = SubscriptionPlanCreateDTO(
        company_id=uuid4(),
        service_id=uuid4(),
        name='A',
        price=Decimal('1'),
    )
    repo.create_plan.return_value = AsyncMock()
    await service.create_plan(dto)
    repo.create_plan.assert_awaited_once_with(dto)


@pytest.mark.asyncio
async def test_service_get_list_update_delete_delegates():
    repo = AsyncMock()
    service = SubscriptionPlanService(repo)
    cid, pid = uuid4(), uuid4()
    p = PaginationParamsDTO()

    repo.get_plan.return_value = None
    assert await service.get_plan(pid, cid) is None
    assert await service.get_plan(pid, cid, active_only=True) is None

    repo.list_plans.return_value = []
    assert await service.list_plans(p, cid) == []
    assert await service.list_plans(p, cid, active_only=True) == []

    u = SubscriptionPlanUpdateDTO(name='B')
    repo.update_plan.return_value = None
    assert await service.update_plan(pid, u, cid) is None

    repo.delete_plan.return_value = True
    assert await service.delete_plan(pid, cid) is True

    repo.service_belongs_to_company.return_value = True
    assert await service.service_belongs_to_company(uuid4(), cid) is True
