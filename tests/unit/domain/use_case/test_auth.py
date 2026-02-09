from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from src.domain.dtos.auth import OwnerAuthDTO, OwnerLoginDTO
from src.domain.execptions.auth import InvalidCredentialsException
from src.domain.use_case.auth import AuthUseCase

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_login_owner_raises_when_owner_not_found():
    owner_service = AsyncMock()
    owner_service.get_owner_auth_by_email.return_value = None
    use_case = AuthUseCase(owner_service)

    with pytest.raises(InvalidCredentialsException):
        await use_case.login_owner(
            OwnerLoginDTO(email='john@example.com', password='plain')
        )


@pytest.mark.asyncio
async def test_login_owner_raises_when_password_invalid():
    owner_service = AsyncMock()
    owner_service.get_owner_auth_by_email.return_value = OwnerAuthDTO(
        id=uuid4(), password='hashed'
    )
    use_case = AuthUseCase(owner_service)

    with patch('src.domain.use_case.auth.verify_password', return_value=False):
        with pytest.raises(InvalidCredentialsException):
            await use_case.login_owner(
                OwnerLoginDTO(email='john@example.com', password='plain')
            )


@pytest.mark.asyncio
async def test_login_owner_returns_token_on_success():
    owner_id = uuid4()
    owner_service = AsyncMock()
    owner_service.get_owner_auth_by_email.return_value = OwnerAuthDTO(
        id=owner_id, password='hashed'
    )
    use_case = AuthUseCase(owner_service)

    with (
        patch('src.domain.use_case.auth.verify_password', return_value=True),
        patch('src.domain.use_case.auth.create_owner_access_token', return_value='tok'),
    ):
        token = await use_case.login_owner(
            OwnerLoginDTO(email='john@example.com', password='plain')
        )

    assert token.access_token == 'tok'
    assert token.token_type == 'bearer'
