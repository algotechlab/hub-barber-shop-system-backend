from unittest.mock import AsyncMock

import pytest
from src.domain.execptions.auth import InvalidCredentialsException
from src.interface.api.v1.controller.auth import AuthController
from src.interface.api.v1.dependencies.auth import get_auth_controller
from src.interface.api.v1.dependencies.common.session import get_verified_session
from src.main import app

URL_LOGIN = '/api/v1/auth/login'


@pytest.fixture
def override_dependency_auth():
    mock_controller = AsyncMock(spec=AuthController)
    mock_session = AsyncMock()

    async def override_get_verified_session():
        yield mock_session

    def override_get_auth_controller():
        return mock_controller

    app.dependency_overrides[get_verified_session] = override_get_verified_session
    app.dependency_overrides[get_auth_controller] = override_get_auth_controller
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
class TestAuthRoutes:
    def test_login_returns_200(self, client, override_dependency_auth):
        override_dependency_auth.login_owner.return_value = {
            'access_token': 'tok',
            'token_type': 'bearer',
        }

        response = client.post(
            URL_LOGIN, json={'email': 'john@example.com', 'password': 'plain'}
        )

        _assert_status(response, 200)
        data = response.json()
        assert data['access_token'] == 'tok'
        assert data['token_type'] == 'bearer'

    def test_login_invalid_credentials_returns_401(
        self, client, override_dependency_auth
    ):
        override_dependency_auth.login_owner.side_effect = InvalidCredentialsException(
            'Credenciais inválidas'
        )

        response = client.post(
            URL_LOGIN, json={'email': 'john@example.com', 'password': 'wrong'}
        )

        _assert_status(response, 401)
        data = response.json()
        assert data['code'] == 'INVALID_CREDENTIALS'
