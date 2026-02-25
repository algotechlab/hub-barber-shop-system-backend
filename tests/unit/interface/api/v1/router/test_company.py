from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import Request
from src.interface.api.v1.controller.company import CompanyController
from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee_or_owner,
    require_current_owner,
)
from src.interface.api.v1.dependencies.common.session import get_verified_session
from src.interface.api.v1.dependencies.company import get_company_controller
from src.main import app

URL_COMPANY = '/api/v1/company'


@pytest.fixture
def override_dependency_company():
    mock_controller = AsyncMock(spec=CompanyController)
    mock_session = AsyncMock()

    async def override_get_verified_session():
        yield mock_session

    def override_get_company_controller():
        return mock_controller

    async def override_require_current_owner(request: Request):
        request.state.owner_id = uuid4()
        return request.state.owner_id

    async def override_require_current_employee_or_owner(request: Request):
        request.state.owner_id = uuid4()
        return request.state.owner_id

    app.dependency_overrides[get_verified_session] = override_get_verified_session
    app.dependency_overrides[get_company_controller] = override_get_company_controller
    app.dependency_overrides[require_current_owner] = override_require_current_owner
    app.dependency_overrides[require_current_employee_or_owner] = (
        override_require_current_employee_or_owner
    )
    yield mock_controller
    app.dependency_overrides.clear()


def _assert_status(response, expected: int, msg_prefix: str = ''):
    if response.status_code != expected:
        body = response.json() if response.content else response.text
        raise AssertionError(
            f'{msg_prefix}Expected status {expected}, '
            f'got {response.status_code}. Body: {body}'
        )


@pytest.mark.unit
class TestCompanyRoutes:
    def test_create_company_returns_201(self, client, override_dependency_company):
        company_id = uuid4()
        owner_id = uuid4()
        override_dependency_company.create_company.return_value = {
            'id': str(company_id),
            'name': 'N',
            'slug': 's',
            'is_active': True,
            'owner_id': str(owner_id),
        }

        response = client.post(
            URL_COMPANY,
            json={'name': 'N', 'slug': 's', 'is_active': True},
            headers={'Authorization': 'Bearer tok'},
        )

        _assert_status(response, 201)

    def test_get_company_returns_200(self, client, override_dependency_company):
        company_id = uuid4()
        owner_id = uuid4()
        override_dependency_company.get_company.return_value = {
            'id': str(company_id),
            'name': 'N',
            'slug': 's',
            'is_active': True,
            'owner_id': str(owner_id),
        }

        response = client.get(
            f'{URL_COMPANY}/{company_id}',
            headers={'Authorization': 'Bearer tok'},
        )

        _assert_status(response, 200)

    def test_list_companies_returns_200(self, client, override_dependency_company):
        override_dependency_company.list_companies.return_value = []

        response = client.get(URL_COMPANY, headers={'Authorization': 'Bearer tok'})

        _assert_status(response, 200)
        assert response.json() == []

    def test_delete_company_returns_204(self, client, override_dependency_company):
        override_dependency_company.delete_company.return_value = None
        company_id = uuid4()

        response = client.delete(
            f'{URL_COMPANY}/{company_id}',
            headers={'Authorization': 'Bearer tok'},
        )

        _assert_status(response, 204)
