import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from src.interface.api.v1.controller.user_subscription import UserSubscriptionController
from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee,
    require_current_user,
)
from src.interface.api.v1.dependencies.user_subscription import (
    get_user_subscription_controller,
)
from src.interface.api.v1.schema.user_subscription import (
    ActivateUserSubscriptionAfterPaymentSchema,
    CreateUserSubscriptionSchema,
    UserSubscriptionOutSchema,
    UserSubscriptionWithPlanAndClientOutSchema,
    UserSubscriptionWithPlanOutSchema,
)
from src.main import app

URL = '/api/v1/user-subscriptions'
STATUS_200, STATUS_201 = 200, 201


def _install_user():
    mock_controller = AsyncMock(spec=UserSubscriptionController)
    app.dependency_overrides[get_user_subscription_controller] = lambda: mock_controller

    async def as_user(request: Request):
        request.state.company_id = uuid.uuid4()
        request.state.user_id = uuid.uuid4()
        return request.state.user_id

    app.dependency_overrides[require_current_user] = as_user
    return mock_controller


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.mark.unit
class TestUserSubscriptionRoutes:
    def test_post_201(self, client):
        m = _install_user()
        now = datetime.now(timezone.utc)
        m.create.return_value = UserSubscriptionOutSchema(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            subscription_plan_id=uuid.uuid4(),
            company_id=uuid.uuid4(),
            status='PENDING_PAYMENT',
            started_at=now,
            ended_at=None,
            external_subscription_id=None,
            payment_at=None,
            payment_method=None,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )
        r = client.post(
            URL,
            json=CreateUserSubscriptionSchema(
                subscription_plan_id=uuid.uuid4()
            ).model_dump(mode='json'),
        )
        assert r.status_code == STATUS_201, r.json()
        app.dependency_overrides.clear()

    def test_get_me_200(self, client):
        m = _install_user()
        now = datetime.now(timezone.utc)
        m.list_mine.return_value = [
            UserSubscriptionWithPlanOutSchema(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                subscription_plan_id=uuid.uuid4(),
                company_id=uuid.uuid4(),
                status='ACTIVE',
                started_at=now,
                ended_at=None,
                external_subscription_id=None,
                payment_at=None,
                payment_method=None,
                created_at=now,
                updated_at=now,
                is_deleted=False,
                plan_name='A',
                plan_price=Decimal('1'),
                plan_description=None,
                service_ids=[uuid.uuid4()],
                plan_product_lines=[],
                plan_uses_per_month=2,
            )
        ]
        r = client.get(f'{URL}/me')
        assert r.status_code == STATUS_200
        app.dependency_overrides.clear()


def _install_employee():
    mock_controller = AsyncMock(spec=UserSubscriptionController)
    app.dependency_overrides[get_user_subscription_controller] = lambda: mock_controller

    async def as_employee(request: Request):
        request.state.company_id = uuid.uuid4()
        request.state.employee_id = uuid.uuid4()
        return request.state.employee_id

    app.dependency_overrides[require_current_employee] = as_employee
    return mock_controller


@pytest.mark.unit
class TestUserSubscriptionEmployeeRoutes:
    def test_get_pending_200(self, client):
        m = _install_employee()
        now = datetime.now(timezone.utc)
        m.list_pending.return_value = [
            UserSubscriptionWithPlanAndClientOutSchema(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                subscription_plan_id=uuid.uuid4(),
                company_id=uuid.uuid4(),
                status='PENDING_PAYMENT',
                started_at=now,
                ended_at=None,
                external_subscription_id=None,
                payment_at=None,
                payment_method=None,
                created_at=now,
                updated_at=now,
                is_deleted=False,
                plan_name='A',
                plan_price=Decimal('1'),
                plan_description=None,
                service_ids=[uuid.uuid4()],
                plan_product_lines=[],
                plan_uses_per_month=2,
                client_name='Maria',
            )
        ]
        r = client.get(f'{URL}/pending')
        assert r.status_code == STATUS_200
        app.dependency_overrides.clear()

    def test_post_activate_after_payment_200(self, client):
        m = _install_employee()
        now = datetime.now(timezone.utc)
        sid = uuid.uuid4()
        m.activate_after_payment.return_value = UserSubscriptionOutSchema(
            id=sid,
            user_id=uuid.uuid4(),
            subscription_plan_id=uuid.uuid4(),
            company_id=uuid.uuid4(),
            status='ACTIVE',
            started_at=now,
            ended_at=None,
            external_subscription_id='x',
            payment_at=now,
            payment_method='PIX',
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )
        r = client.post(
            f'{URL}/{sid}/activate-after-payment',
            json=ActivateUserSubscriptionAfterPaymentSchema(
                payment_method='PIX',
                external_subscription_id='x',
            ).model_dump(mode='json'),
        )
        assert r.status_code == STATUS_200, r.json()
        app.dependency_overrides.clear()
