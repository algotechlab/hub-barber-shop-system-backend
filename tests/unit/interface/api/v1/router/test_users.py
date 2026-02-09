from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.interface.api.v1.controller.users import UsersController
from src.interface.api.v1.dependencies.common.pagination import get_pagination_params
from src.interface.api.v1.dependencies.common.session import get_verified_session
from src.interface.api.v1.dependencies.users import get_users_controller
from src.main import app

URL_USERS = '/api/v1/users'


@pytest.fixture
def override_dependency_users():
    mock_controller = AsyncMock(spec=UsersController)
    mock_session = AsyncMock()

    async def override_get_verified_session():
        yield mock_session

    def override_get_users_controller():
        return mock_controller

    def override_get_pagination_params():
        return PaginationParamsDTO()

    app.dependency_overrides[get_verified_session] = override_get_verified_session
    app.dependency_overrides[get_users_controller] = override_get_users_controller
    app.dependency_overrides[get_pagination_params] = override_get_pagination_params
    yield mock_controller
    app.dependency_overrides.clear()


def _install_overrides():
    """Instala overrides nas mesmas funções que as rotas de users usam."""
    mock_controller = AsyncMock(spec=UsersController)
    mock_session = AsyncMock()

    async def override_session():
        yield mock_session

    # Importante: o override NÃO pode ter parâmetro `session` sem Depends(),
    # senão o FastAPI interpreta como query param obrigatório e retorna 422.
    def override_controller():
        return mock_controller

    def override_pagination():
        return PaginationParamsDTO()

    app.dependency_overrides[get_verified_session] = override_session
    app.dependency_overrides[get_users_controller] = override_controller
    app.dependency_overrides[get_pagination_params] = override_pagination
    return mock_controller


def _assert_status(response, expected: int, msg_prefix: str = ''):
    if response.status_code != expected:
        body = response.json() if response.content else response.text
        raise AssertionError(
            f'{msg_prefix}Expected status {expected}, '
            f'got {response.status_code}. Body: {body}'
        )


@pytest.mark.unit
class TestUsersRoutes:
    def test_list_users_returns_200(self, client, override_dependency_users):
        override_dependency_users.list_users.return_value = []
        response = client.get(URL_USERS)
        _assert_status(response, 200)
        assert response.json() == []

    def test_list_users_with_pagination(
        self, client, override_dependency_users, generate_user_out_schema
    ):
        override_dependency_users.list_users.return_value = [generate_user_out_schema]
        response = client.get(f'{URL_USERS}?filter_by=name&filter_value=John')
        _assert_status(response, 200)
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == 'John Doe'
        assert data[0]['email'] == 'john.doe@example.com'

    def test_add_users_returns_201(
        self, client, override_dependency_users, generate_uuid, generate_user_out_schema
    ):
        override_dependency_users.create_user.return_value = generate_user_out_schema
        payload = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'password': 'password',
            'company_id': str(generate_uuid),
        }
        response = client.post(URL_USERS, json=payload)
        _assert_status(response, 201)
        data = response.json()
        assert data['name'] == payload['name']
        assert data['email'] == payload['email']

    def test_update_user_returns_200(
        self, client, override_dependency_users, generate_uuid, generate_user_out_schema
    ):
        override_dependency_users.update_user.return_value = generate_user_out_schema
        response = client.patch(
            f'{URL_USERS}/{generate_uuid}',
            json={'name': 'Updated Name'},
        )
        _assert_status(response, 200)
        data = response.json()
        assert data['name'] == generate_user_out_schema.name

    def test_delete_user_returns_204(
        self, client, override_dependency_users, generate_uuid
    ):
        override_dependency_users.delete_user.return_value = True
        response = client.delete(f'{URL_USERS}/{generate_uuid}')
        _assert_status(response, 204)
