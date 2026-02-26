from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.interface.api.v1.controller.company import CompanyController
from src.interface.api.v1.dependencies.common.session import get_verified_session
from src.interface.api.v1.dependencies.company import get_company_controller
from src.main import app

URL_SLUG_COMPANIES = '/api/v1/slug-companies'


@pytest.fixture
def override_dependency_slug_companies():
    mock_controller = AsyncMock(spec=CompanyController)
    mock_session = AsyncMock()

    async def override_get_verified_session():
        yield mock_session

    def override_get_company_controller():
        return mock_controller

    app.dependency_overrides[get_verified_session] = override_get_verified_session
    app.dependency_overrides[get_company_controller] = override_get_company_controller
    yield mock_controller
    app.dependency_overrides.clear()


@pytest.mark.unit
class TestSlugCompaniesRoutes:
    def test_list_companies_slug_returns_200(
        self, client, override_dependency_slug_companies
    ):
        status_code = 200
        override_dependency_slug_companies.list_companies_slug.return_value = [
            {
                'id': str(uuid4()),
                'name': 'N',
                'slug': 'slug-x',
                'is_active': True,
                'owner_id': str(uuid4()),
            }
        ]

        response = client.get(f'{URL_SLUG_COMPANIES}/slug-x')

        assert response.status_code == status_code
        assert response.json()[0]['slug'] == 'slug-x'
