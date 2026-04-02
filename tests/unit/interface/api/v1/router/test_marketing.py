from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import Request
from src.interface.api.v1.controller.marketing import MarketingController
from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee_or_owner,
)
from src.interface.api.v1.dependencies.common.session import get_verified_session
from src.interface.api.v1.dependencies.marketing import (
    get_marketing_controller,
    resolve_marketing_company_id,
)
from src.interface.api.v1.schema.marketing import (
    MessageTemplateOutSchema,
    WhatsappConnectionOutSchema,
)
from src.main import app

URL_BASE = '/api/v1/marketing'


@pytest.fixture
def override_marketing():
    mock_controller = AsyncMock(spec=MarketingController)
    mock_session = AsyncMock()

    async def override_get_verified_session():
        yield mock_session

    async def override_auth(request: Request):
        request.state.company_id = uuid4()
        return uuid4()

    def override_get_marketing_controller():
        return mock_controller

    async def override_company_id():
        return uuid4()

    overrides = app.dependency_overrides
    overrides[get_verified_session] = override_get_verified_session
    overrides[get_marketing_controller] = override_get_marketing_controller
    overrides[require_current_employee_or_owner] = override_auth
    overrides[resolve_marketing_company_id] = override_company_id
    yield mock_controller
    app.dependency_overrides.clear()


def _assert_status(response, expected: int):
    if response.status_code != expected:
        body = response.json() if response.content else response.text
        raise AssertionError(f'Expected {expected}, got {response.status_code}: {body}')


@pytest.mark.unit
class TestMarketingRoutes:
    def test_get_message_template_200(self, client, override_marketing):
        override_marketing.get_message_template.return_value = MessageTemplateOutSchema(
            template='hi'
        )
        r = client.get(
            f'{URL_BASE}/message-template',
            headers={'Authorization': 'Bearer t'},
        )
        _assert_status(r, 200)
        assert r.json()['template'] == 'hi'

    def test_put_message_template_200(self, client, override_marketing):
        override_marketing.save_message_template.return_value = (
            MessageTemplateOutSchema(template='saved')
        )
        r = client.put(
            f'{URL_BASE}/message-template',
            headers={'Authorization': 'Bearer t'},
            json={'template': 'saved'},
        )
        _assert_status(r, 200)

    def test_get_whatsapp_connection_200(self, client, override_marketing):
        override_marketing.get_whatsapp_connection.return_value = (
            WhatsappConnectionOutSchema(
                state='open',
                status='open',
                qr_base64=None,
                source='api',
            )
        )
        r = client.get(
            f'{URL_BASE}/whatsapp/connection',
            headers={'Authorization': 'Bearer t'},
        )
        _assert_status(r, 200)

    def test_get_inactive_clients_200(self, client, override_marketing):
        override_marketing.get_inactive_clients.return_value = {
            'users': [],
            'schedules': [],
        }
        r = client.get(
            f'{URL_BASE}/inactive-clients',
            headers={'Authorization': 'Bearer t'},
        )
        _assert_status(r, 200)

    def test_get_inactive_clients_422_min_max(self, client, override_marketing):
        r = client.get(
            f'{URL_BASE}/inactive-clients?min_days=10&max_days=5',
            headers={'Authorization': 'Bearer t'},
        )
        _assert_status(r, 422)

    def test_post_send_message_204(self, client, override_marketing):
        r = client.post(
            f'{URL_BASE}/send-message',
            headers={'Authorization': 'Bearer t'},
            json={'number': '5511999999999', 'text': None},
        )
        _assert_status(r, 204)
