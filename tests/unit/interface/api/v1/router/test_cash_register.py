import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import Request
from src.interface.api.v1.controller.cash_register import CashRegisterController
from src.interface.api.v1.dependencies.cash_register import (
    get_cash_register_controller,
)
from src.interface.api.v1.dependencies.common.auth import require_current_employee
from src.main import app

URL_BASE = '/api/v1/cash-register'
STATUS_CODE_200 = 200
STATUS_CODE_201 = 201


def _install_overrides():
    mock_controller = AsyncMock(spec=CashRegisterController)

    def override_controller():
        return mock_controller

    app.dependency_overrides[get_cash_register_controller] = override_controller

    async def override_employee(request: Request):
        request.state.company_id = uuid.uuid4()
        request.state.employee_id = uuid.uuid4()
        return request.state.employee_id

    app.dependency_overrides[require_current_employee] = override_employee
    return mock_controller


@pytest.fixture
def override_cash_register():
    mock_controller = _install_overrides()
    yield mock_controller
    app.dependency_overrides.clear()


def _session_body(sid=None):
    sid = sid or str(uuid.uuid4())
    return {
        'id': sid,
        'company_id': str(uuid.uuid4()),
        'opened_by': str(uuid.uuid4()),
        'closed_by': None,
        'opened_at': '2026-04-22T10:00:00Z',
        'closed_at': None,
        'opening_balance': '100.00',
        'closing_balance': None,
        'expected_balance': None,
        'opening_notes': None,
        'closing_notes': None,
        'created_at': '2026-04-22T10:00:00Z',
        'updated_at': '2026-04-22T10:00:00Z',
        'is_deleted': False,
    }


@pytest.mark.unit
class TestCashRegisterRoutes:
    def test_open_session_returns_201(self, client, override_cash_register):
        override_cash_register.open_session.return_value = _session_body()

        response = client.post(
            f'{URL_BASE}/sessions',
            json={'opening_balance': '100.00'},
        )

        assert response.status_code == STATUS_CODE_201, response.text

    def test_list_sessions_returns_200(self, client, override_cash_register):
        override_cash_register.list_sessions.return_value = []

        response = client.get(f'{URL_BASE}/sessions')

        assert response.status_code == STATUS_CODE_200
        assert response.json() == []

    def test_get_open_returns_200(self, client, override_cash_register):
        override_cash_register.get_open_session.return_value = _session_body()

        response = client.get(f'{URL_BASE}/sessions/open')

        assert response.status_code == STATUS_CODE_200

    def test_get_open_summary_returns_200(self, client, override_cash_register):
        sid = str(uuid.uuid4())
        base = _session_body(sid)
        override_cash_register.get_open_summary.return_value = {
            'session': base,
            'sales_total': '0',
            'expenses_total': '0',
            'supplies_total': '0',
            'withdrawals_total': '0',
            'expected_balance': '100.00',
            'window_end_at': '2026-04-22T12:00:00Z',
            'balance_difference': None,
        }

        response = client.get(f'{URL_BASE}/sessions/open/summary')

        assert response.status_code == STATUS_CODE_200

    def test_get_session_summary_returns_200(self, client, override_cash_register):
        sid = uuid.uuid4()
        base = _session_body(str(sid))
        override_cash_register.get_session_summary.return_value = {
            'session': base,
            'sales_total': '0',
            'expenses_total': '0',
            'supplies_total': '0',
            'withdrawals_total': '0',
            'expected_balance': '100.00',
            'window_end_at': '2026-04-22T12:00:00Z',
            'balance_difference': None,
        }

        response = client.get(f'{URL_BASE}/sessions/{sid}/summary')

        assert response.status_code == STATUS_CODE_200

    def test_close_returns_200(self, client, override_cash_register):
        sid = uuid.uuid4()
        body = _session_body(str(sid))
        body['closing_balance'] = '100.00'
        body['closed_at'] = '2026-04-22T18:00:00Z'
        override_cash_register.close_session.return_value = body

        response = client.post(
            f'{URL_BASE}/sessions/{sid}/close',
            json={'closing_balance': '100.00'},
        )

        assert response.status_code == STATUS_CODE_200

    def test_adjustment_returns_201(self, client, override_cash_register):
        sid = uuid.uuid4()
        override_cash_register.register_adjustment.return_value = {
            'id': str(uuid.uuid4()),
            'session_id': str(sid),
            'company_id': str(uuid.uuid4()),
            'created_by': str(uuid.uuid4()),
            'kind': 'SUPPLY',
            'amount': '10.00',
            'description': 'suprimento',
            'created_at': '2026-04-22T10:00:00Z',
            'updated_at': '2026-04-22T10:00:00Z',
            'is_deleted': False,
        }

        response = client.post(
            f'{URL_BASE}/sessions/{sid}/adjustments',
            json={
                'kind': 'SUPPLY',
                'amount': '10.00',
                'description': 'suprimento',
            },
        )

        assert response.status_code == STATUS_CODE_201
