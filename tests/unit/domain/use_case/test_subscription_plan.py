from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.subscription_plan import (
    SubscriptionPlanCreateDTO,
    SubscriptionPlanOutDTO,
    SubscriptionPlanProductLineOutDTO,
    SubscriptionPlanUpdateDTO,
)
from src.domain.exceptions.subscription import (
    SubscriptionPlanNotFoundException,
    SubscriptionPlanServiceMismatchException,
)
from src.domain.use_case.subscription_plan import SubscriptionPlanUseCase

pytestmark = pytest.mark.unit


def _plan(company_id):
    now = datetime.now(timezone.utc)
    return SubscriptionPlanOutDTO(
        id=uuid4(),
        company_id=company_id,
        name='P',
        description=None,
        service_ids=[uuid4()],
        product_lines=[],
        price=Decimal('10'),
        uses_per_month=2,
        is_active=True,
        created_at=now,
        updated_at=now,
        is_deleted=False,
    )


@pytest.mark.asyncio
async def test_create_plan_raises_when_service_mismatch():
    svc = AsyncMock()
    svc.service_belongs_to_company.return_value = False
    uc = SubscriptionPlanUseCase(svc)
    dto = SubscriptionPlanCreateDTO(
        company_id=uuid4(),
        service_ids=[uuid4()],
        name='A',
        price=Decimal('1'),
    )
    with pytest.raises(SubscriptionPlanServiceMismatchException):
        await uc.create_plan(dto)
    svc.create_plan.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_plan_success():
    svc = AsyncMock()
    cid = uuid4()
    expected = _plan(cid)
    svc.service_belongs_to_company.return_value = True
    svc.create_plan.return_value = expected
    uc = SubscriptionPlanUseCase(svc)
    dto = SubscriptionPlanCreateDTO(
        company_id=cid,
        service_ids=expected.service_ids,
        name='A',
        price=Decimal('1'),
    )
    r = await uc.create_plan(dto)
    assert r == expected


@pytest.mark.asyncio
async def test_create_plan_raises_when_product_mismatch():
    svc = AsyncMock()
    cid = uuid4()
    pid = uuid4()
    svc.service_belongs_to_company.return_value = True
    svc.product_belongs_to_company.return_value = False
    uc = SubscriptionPlanUseCase(svc)
    dto = SubscriptionPlanCreateDTO(
        company_id=cid,
        service_ids=[uuid4()],
        name='A',
        price=Decimal('1'),
        product_lines=[
            SubscriptionPlanProductLineOutDTO(product_id=pid, quantity=2),
        ],
    )
    with pytest.raises(SubscriptionPlanServiceMismatchException):
        await uc.create_plan(dto)
    svc.create_plan.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_plan_with_product_lines_validates_products():
    svc = AsyncMock()
    cid = uuid4()
    expected = _plan(cid)
    pid = uuid4()
    svc.service_belongs_to_company.return_value = True
    svc.product_belongs_to_company.return_value = True
    svc.create_plan.return_value = expected
    uc = SubscriptionPlanUseCase(svc)
    dto = SubscriptionPlanCreateDTO(
        company_id=cid,
        service_ids=expected.service_ids,
        name='A',
        price=Decimal('1'),
        product_lines=[
            SubscriptionPlanProductLineOutDTO(product_id=pid, quantity=1),
        ],
    )
    r = await uc.create_plan(dto)
    assert r == expected
    svc.product_belongs_to_company.assert_awaited_once_with(pid, cid)


@pytest.mark.asyncio
async def test_get_plan_not_found():
    svc = AsyncMock()
    svc.get_plan.return_value = None
    uc = SubscriptionPlanUseCase(svc)
    with pytest.raises(SubscriptionPlanNotFoundException):
        await uc.get_plan(uuid4(), uuid4())


@pytest.mark.asyncio
async def test_get_plan_active_only_delegates():
    svc = AsyncMock()
    cid = uuid4()
    p = _plan(cid)
    svc.get_plan.return_value = p
    uc = SubscriptionPlanUseCase(svc)
    r = await uc.get_plan(p.id, cid, active_only=True)
    assert r == p
    svc.get_plan.assert_awaited_once_with(p.id, cid, active_only=True)


@pytest.mark.asyncio
async def test_list_plans_delegates():
    svc = AsyncMock()
    svc.list_plans.return_value = []
    uc = SubscriptionPlanUseCase(svc)
    page = PaginationParamsDTO()
    cid = uuid4()
    r = await uc.list_plans(page, cid, active_only=True)
    assert r == []
    svc.list_plans.assert_awaited_once_with(page, cid, active_only=True)


@pytest.mark.asyncio
async def test_update_plan_service_mismatch():
    svc = AsyncMock()
    uc = SubscriptionPlanUseCase(svc)
    sid, cid = uuid4(), uuid4()
    data = SubscriptionPlanUpdateDTO(service_ids=[sid])
    svc.service_belongs_to_company.return_value = False
    with pytest.raises(SubscriptionPlanServiceMismatchException):
        await uc.update_plan(uuid4(), data, cid)


@pytest.mark.asyncio
async def test_update_plan_not_found():
    svc = AsyncMock()
    svc.service_belongs_to_company.return_value = True
    svc.update_plan.return_value = None
    uc = SubscriptionPlanUseCase(svc)
    with pytest.raises(SubscriptionPlanNotFoundException):
        await uc.update_plan(uuid4(), SubscriptionPlanUpdateDTO(name='X'), uuid4())


@pytest.mark.asyncio
async def test_update_plan_success():
    svc = AsyncMock()
    cid = uuid4()
    out = _plan(cid)
    svc.update_plan.return_value = out
    uc = SubscriptionPlanUseCase(svc)
    r = await uc.update_plan(out.id, SubscriptionPlanUpdateDTO(name='Y'), cid)
    assert r == out


@pytest.mark.asyncio
async def test_update_plan_raises_when_product_mismatch():
    svc = AsyncMock()
    cid, pid = uuid4(), uuid4()
    svc.service_belongs_to_company.return_value = True
    svc.product_belongs_to_company.return_value = False
    uc = SubscriptionPlanUseCase(svc)
    data = SubscriptionPlanUpdateDTO(
        product_lines=[SubscriptionPlanProductLineOutDTO(product_id=pid, quantity=1)],
    )
    with pytest.raises(SubscriptionPlanServiceMismatchException):
        await uc.update_plan(uuid4(), data, cid)
    svc.update_plan.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_plan_with_product_lines_validates_products():
    svc = AsyncMock()
    cid = uuid4()
    out = _plan(cid)
    pid = uuid4()
    svc.service_belongs_to_company.return_value = True
    svc.product_belongs_to_company.return_value = True
    svc.update_plan.return_value = out
    uc = SubscriptionPlanUseCase(svc)
    data = SubscriptionPlanUpdateDTO(
        product_lines=[SubscriptionPlanProductLineOutDTO(product_id=pid, quantity=1)],
    )
    r = await uc.update_plan(out.id, data, cid)
    assert r == out
    svc.product_belongs_to_company.assert_awaited_once_with(pid, cid)


@pytest.mark.asyncio
async def test_delete_plan_not_found():
    svc = AsyncMock()
    svc.delete_plan.return_value = False
    uc = SubscriptionPlanUseCase(svc)
    with pytest.raises(SubscriptionPlanNotFoundException):
        await uc.delete_plan(uuid4(), uuid4())


@pytest.mark.asyncio
async def test_delete_plan_success():
    svc = AsyncMock()
    svc.delete_plan.return_value = True
    uc = SubscriptionPlanUseCase(svc)
    assert await uc.delete_plan(uuid4(), uuid4()) is True
