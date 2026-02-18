from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from src.domain.dtos.auth import (
    EmployeeAuthDTO,
    EmployeeLoginDTO,
    OwnerAuthDTO,
    OwnerLoginDTO,
    UserAuthDTO,
    UserLoginDTO,
)
from src.domain.execptions.auth import InvalidCredentialsException
from src.domain.use_case.auth import AuthUseCase

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_login_owner_raises_when_owner_not_found():
    owner_service = AsyncMock()
    owner_service.get_owner_auth_by_email.return_value = None
    use_case = AuthUseCase(owner_service, AsyncMock(), AsyncMock())

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
    use_case = AuthUseCase(owner_service, AsyncMock(), AsyncMock())

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
    use_case = AuthUseCase(owner_service, AsyncMock(), AsyncMock())

    with (
        patch('src.domain.use_case.auth.verify_password', return_value=True),
        patch('src.domain.use_case.auth.create_owner_access_token', return_value='tok'),
    ):
        token = await use_case.login_owner(
            OwnerLoginDTO(email='john@example.com', password='plain')
        )

    assert token.access_token == 'tok'
    assert token.token_type == 'bearer'


@pytest.mark.asyncio
async def test_login_employee_raises_when_employee_not_found():
    employee_service = AsyncMock()
    employee_service.get_employee_auth_by_phone.return_value = None
    use_case = AuthUseCase(AsyncMock(), employee_service, AsyncMock())

    with pytest.raises(InvalidCredentialsException):
        await use_case.login_employee(
            EmployeeLoginDTO(phone='11999999999', password='plain')
        )


@pytest.mark.asyncio
async def test_login_employee_raises_when_password_invalid():
    employee_service = AsyncMock()
    employee_service.get_employee_auth_by_phone.return_value = EmployeeAuthDTO(
        id=uuid4(), name='John', password='hashed', company_id=uuid4()
    )
    use_case = AuthUseCase(AsyncMock(), employee_service, AsyncMock())

    with patch('src.domain.use_case.auth.verify_password', return_value=False):
        with pytest.raises(InvalidCredentialsException):
            await use_case.login_employee(
                EmployeeLoginDTO(phone='11999999999', password='plain')
            )


@pytest.mark.asyncio
async def test_login_employee_returns_token_with_company_on_success():
    employee_id = uuid4()
    company_id = uuid4()
    employee_service = AsyncMock()
    employee_service.get_employee_auth_by_phone.return_value = EmployeeAuthDTO(
        id=employee_id, name='John', password='hashed', company_id=company_id
    )
    use_case = AuthUseCase(AsyncMock(), employee_service, AsyncMock())

    with (
        patch('src.domain.use_case.auth.verify_password', return_value=True),
        patch('src.domain.use_case.auth.create_access_token', return_value='tok'),
    ):
        token = await use_case.login_employee(
            EmployeeLoginDTO(phone='11999999999', password='plain')
        )

    assert token.access_token == 'tok'
    assert token.company_id == company_id
    assert token.id == employee_id
    assert token.name == 'John'


@pytest.mark.asyncio
async def test_login_user_raises_when_user_not_found():
    users_service = AsyncMock()
    users_service.get_user_auth_by_phone.return_value = None
    use_case = AuthUseCase(AsyncMock(), AsyncMock(), users_service)

    with pytest.raises(InvalidCredentialsException):
        await use_case.login_user(UserLoginDTO(phone='11999999999'))


@pytest.mark.asyncio
async def test_login_user_returns_token_with_company_on_success():
    user_id = uuid4()
    company_id = uuid4()
    users_service = AsyncMock()
    users_service.get_user_auth_by_phone.return_value = UserAuthDTO(
        id=user_id, name='John', company_id=company_id
    )
    use_case = AuthUseCase(AsyncMock(), AsyncMock(), users_service)

    with patch('src.domain.use_case.auth.create_access_token', return_value='tok'):
        token = await use_case.login_user(UserLoginDTO(phone='11999999999'))

    assert token.access_token == 'tok'
    assert token.company_id == company_id
    assert token.id == user_id
    assert token.name == 'John'
