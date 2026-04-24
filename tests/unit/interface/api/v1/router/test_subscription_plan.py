import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from src.interface.api.v1.controller.subscription_plan import SubscriptionPlanController
from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee,
    require_current_employee_or_user,
)
from src.interface.api.v1.dependencies.subscription_plan import (
    get_subscription_plan_controller,
)
from src.interface.api.v1.schema.subscription_plan import (
    CreateSubscriptionPlanSchema,
    SubscriptionPlanOutSchema,
    UpdateSubscriptionPlanSchema,
)
from src.main import app

URL = '/api/v1/subscription-plans'
STATUS_200, STATUS_201, STATUS_204 = 200, 201, 204


def _out():
    now = datetime.now(timezone.utc)
    return SubscriptionPlanOutSchema(
        id=uuid.uuid4(),
        company_id=uuid.uuid4(),
        name='A',
        description=None,
        service_ids=[uuid.uuid4()],
        product_lines=[],
        price=Decimal('1'),
        uses_per_month=2,
        is_active=True,
        created_at=now,
        updated_at=now,
        is_deleted=False,
    )


def _install_employee_mode():
    mock_controller = AsyncMock(spec=SubscriptionPlanController)
    app.dependency_overrides[get_subscription_plan_controller] = lambda: mock_controller

    async def emp_or_user(request: Request):
        request.state.company_id = uuid.uuid4()
        request.state.employee_id = uuid.uuid4()
        return request.state.employee_id

    app.dependency_overrides[require_current_employee_or_user] = emp_or_user
    app.dependency_overrides[require_current_employee] = emp_or_user
    return mock_controller


def _install_user_mode():
    mock_controller = AsyncMock(spec=SubscriptionPlanController)
    app.dependency_overrides[get_subscription_plan_controller] = lambda: mock_controller

    async def emp_or_user(request: Request):
        request.state.company_id = uuid.uuid4()
        request.state.user_id = uuid.uuid4()
        return request.state.user_id

    app.dependency_overrides[require_current_employee_or_user] = emp_or_user
    return mock_controller


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.mark.unit
class TestSubscriptionPlanRoutes:
    def test_list_employee_sees_inactive(self, client):
        m = _install_employee_mode()
        m.list_plans.return_value = [_out()]
        r = client.get(URL)
        assert r.status_code == STATUS_200
        m.list_plans.assert_called_once()
        assert m.list_plans.call_args.kwargs.get('active_only') is False
        app.dependency_overrides.clear()

    def test_list_user_active_only(self, client):
        m = _install_user_mode()
        m.list_plans.return_value = [_out()]
        r = client.get(URL)
        assert r.status_code == STATUS_200
        assert m.list_plans.call_args.kwargs.get('active_only') is True
        app.dependency_overrides.clear()

    def test_create_201(self, client):
        m = _install_employee_mode()
        m.create_plan.return_value = _out()
        payload = CreateSubscriptionPlanSchema(
            service_ids=[uuid.uuid4()],
            name='B',
            price=Decimal('2'),
        ).model_dump(mode='json')
        r = client.post(URL, json=payload)
        assert r.status_code == STATUS_201, r.json()
        app.dependency_overrides.clear()

    def test_get_by_id_200(self, client):
        m = _install_employee_mode()
        m.get_plan.return_value = _out()
        pid = uuid.uuid4()
        r = client.get(f'{URL}/{pid}')
        assert r.status_code == STATUS_200
        m.get_plan.assert_called_once()
        app.dependency_overrides.clear()

    def test_patch_200(self, client):
        m = _install_employee_mode()
        m.update_plan.return_value = _out()
        r = client.patch(
            f'{URL}/{uuid.uuid4()}',
            json=UpdateSubscriptionPlanSchema(name='Z').model_dump(),
        )
        assert r.status_code == STATUS_200
        app.dependency_overrides.clear()

    def test_delete_204(self, client):
        m = _install_employee_mode()
        m.delete_plan.return_value = None
        r = client.delete(f'{URL}/{uuid.uuid4()}')
        assert r.status_code == STATUS_204
        app.dependency_overrides.clear()
