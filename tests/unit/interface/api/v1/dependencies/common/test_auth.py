from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import jwt
import pytest
from src.domain.execptions.auth import UnauthorizedException
from src.interface.api.v1.dependencies.common.auth import (
    get_current_employee_id,
    get_current_owner_id,
    get_current_user_id,
    require_current_employee,
    require_current_owner,
    require_current_user,
)
from starlette.requests import Request

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_current_owner_id_raises_when_authorization_missing():
    with pytest.raises(UnauthorizedException, match='Token ausente'):
        await get_current_owner_id(session=AsyncMock(), authorization=None)


@pytest.mark.asyncio
async def test_get_current_owner_id_raises_when_scheme_invalid():
    with pytest.raises(UnauthorizedException, match='Header Authorization inválido'):
        await get_current_owner_id(session=AsyncMock(), authorization='Token abc')


@pytest.mark.asyncio
async def test_get_current_owner_id_raises_when_token_invalid():
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            side_effect=jwt.exceptions.PyJWTError(),
        ),
    ):
        with pytest.raises(UnauthorizedException, match='Token inválido'):
            await get_current_owner_id(session=AsyncMock(), authorization='Bearer x')


@pytest.mark.asyncio
async def test_get_current_owner_id_returns_uuid_when_valid_and_owner_exists():
    owner_id = uuid4()
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    mock_owner_repo = MagicMock()
    mock_owner_repo.get_owner = AsyncMock(return_value=MagicMock())

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={'sub': str(owner_id), 'typ': 'owner'},
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.OwnerRepositoryPostgres',
            return_value=mock_owner_repo,
        ),
    ):
        result = await get_current_owner_id(
            session=AsyncMock(),
            authorization='Bearer token',
        )

    assert result == owner_id
    mock_owner_repo.get_owner.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_current_owner_id_raises_when_sub_missing():
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={'typ': 'owner'},
        ),
    ):
        with pytest.raises(UnauthorizedException, match='Token inválido'):
            await get_current_owner_id(session=AsyncMock(), authorization='Bearer tok')


@pytest.mark.asyncio
async def test_get_current_owner_id_raises_when_sub_not_uuid():
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={'sub': 'not-a-uuid', 'typ': 'owner'},
        ),
    ):
        with pytest.raises(UnauthorizedException, match='Token inválido'):
            await get_current_owner_id(session=AsyncMock(), authorization='Bearer tok')


@pytest.mark.asyncio
async def test_get_current_owner_id_raises_when_owner_does_not_exist():
    owner_id = uuid4()
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    mock_owner_repo = MagicMock()
    mock_owner_repo.get_owner = AsyncMock(return_value=None)

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={'sub': str(owner_id), 'typ': 'owner'},
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.OwnerRepositoryPostgres',
            return_value=mock_owner_repo,
        ),
    ):
        with pytest.raises(UnauthorizedException, match='Owner inválido'):
            await get_current_owner_id(
                session=AsyncMock(),
                authorization='Bearer token',
            )


@pytest.mark.asyncio
async def test_require_current_owner_sets_request_state_owner_id():
    owner_id = uuid4()
    request = Request({
        'type': 'http',
        'headers': [],
        'method': 'GET',
        'path': '/',
        'query_string': b'',
        'scheme': 'http',
        'server': ('test', 80),
        'client': ('test', 1234),
    })

    with patch(
        'src.interface.api.v1.dependencies.common.auth.get_current_owner_id',
        return_value=owner_id,
    ):
        result = await require_current_owner(
            request=request,
            session=AsyncMock(),
            authorization='Bearer token',
        )

    assert result == owner_id
    assert request.state.owner_id == owner_id


@pytest.mark.asyncio
async def test_get_current_employee_id_returns_uuid_when_valid_and_employee_exists():
    employee_id = uuid4()
    company_id = uuid4()
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    mock_employee_repo = MagicMock()
    mock_employee_repo.get_employee = AsyncMock(
        return_value=MagicMock(company_id=company_id)
    )

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={
                'sub': str(employee_id),
                'typ': 'employee',
                'company_id': str(company_id),
            },
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.EmployeeRepositoryPostgres',
            return_value=mock_employee_repo,
        ),
    ):
        result = await get_current_employee_id(
            session=AsyncMock(),
            authorization='Bearer token',
        )

    assert result == employee_id
    mock_employee_repo.get_employee.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_current_employee_id_raises_when_type_mismatch():
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={
                'sub': str(uuid4()),
                'typ': 'user',
                'company_id': str(uuid4()),
            },
        ),
    ):
        with pytest.raises(UnauthorizedException, match='Token inválido'):
            await get_current_employee_id(
                session=AsyncMock(),
                authorization='Bearer token',
            )


@pytest.mark.asyncio
async def test_get_current_employee_id_raises_when_employee_not_found():
    employee_id = uuid4()
    company_id = uuid4()
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    mock_employee_repo = MagicMock()
    mock_employee_repo.get_employee = AsyncMock(return_value=None)

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={
                'sub': str(employee_id),
                'typ': 'employee',
                'company_id': str(company_id),
            },
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.EmployeeRepositoryPostgres',
            return_value=mock_employee_repo,
        ),
    ):
        with pytest.raises(UnauthorizedException, match='Employee inválido'):
            await get_current_employee_id(
                session=AsyncMock(),
                authorization='Bearer token',
            )


@pytest.mark.asyncio
async def test_get_current_employee_id_raises_when_company_id_mismatch():
    employee_id = uuid4()
    company_id = uuid4()
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    mock_employee_repo = MagicMock()
    # Se o company_id do token não bater, o repo (filtrado por company_id) não encontra.
    mock_employee_repo.get_employee = AsyncMock(return_value=None)

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={
                'sub': str(employee_id),
                'typ': 'employee',
                'company_id': str(company_id),
            },
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.EmployeeRepositoryPostgres',
            return_value=mock_employee_repo,
        ),
    ):
        with pytest.raises(UnauthorizedException, match='Employee inválido'):
            await get_current_employee_id(
                session=AsyncMock(),
                authorization='Bearer token',
            )


@pytest.mark.asyncio
async def test_require_current_employee_sets_request_state_employee_and_company():
    employee_id = uuid4()
    company_id = uuid4()
    request = Request({
        'type': 'http',
        'headers': [],
        'method': 'GET',
        'path': '/',
        'query_string': b'',
        'scheme': 'http',
        'server': ('test', 80),
        'client': ('test', 1234),
    })

    mock_employee_repo = MagicMock()
    mock_employee_repo.get_employee = AsyncMock(
        return_value=MagicMock(company_id=company_id)
    )

    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={
                'sub': str(employee_id),
                'typ': 'employee',
                'company_id': str(company_id),
            },
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.EmployeeRepositoryPostgres',
            return_value=mock_employee_repo,
        ),
    ):
        result = await require_current_employee(
            request=request,
            session=AsyncMock(),
            authorization='Bearer token',
        )

    assert result == employee_id
    assert request.state.employee_id == employee_id
    assert request.state.company_id == company_id


@pytest.mark.asyncio
async def test_require_current_employee_raises_when_employee_invalid():
    employee_id = uuid4()
    company_id = uuid4()
    request = Request({
        'type': 'http',
        'headers': [],
        'method': 'GET',
        'path': '/',
        'query_string': b'',
        'scheme': 'http',
        'server': ('test', 80),
        'client': ('test', 1234),
    })

    mock_employee_repo = MagicMock()
    mock_employee_repo.get_employee = AsyncMock(return_value=None)
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={
                'sub': str(employee_id),
                'typ': 'employee',
                'company_id': str(company_id),
            },
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.EmployeeRepositoryPostgres',
            return_value=mock_employee_repo,
        ),
    ):
        with pytest.raises(UnauthorizedException, match='Employee inválido'):
            await require_current_employee(
                request=request,
                session=AsyncMock(),
                authorization='Bearer token',
            )


@pytest.mark.asyncio
async def test_get_current_user_id_returns_uuid_when_valid_and_user_exists():
    user_id = uuid4()
    company_id = uuid4()
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    mock_users_repo = MagicMock()
    mock_users_repo.get_user = AsyncMock(return_value=MagicMock(company_id=company_id))

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={
                'sub': str(user_id),
                'typ': 'user',
                'company_id': str(company_id),
            },
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.UsersRepositoryPostgres',
            return_value=mock_users_repo,
        ),
    ):
        result = await get_current_user_id(
            session=AsyncMock(),
            authorization='Bearer token',
        )

    assert result == user_id
    mock_users_repo.get_user.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_current_user_id_raises_when_user_not_found():
    user_id = uuid4()
    company_id = uuid4()
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    mock_users_repo = MagicMock()
    mock_users_repo.get_user = AsyncMock(return_value=None)

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={
                'sub': str(user_id),
                'typ': 'user',
                'company_id': str(company_id),
            },
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.UsersRepositoryPostgres',
            return_value=mock_users_repo,
        ),
    ):
        with pytest.raises(UnauthorizedException, match='User inválido'):
            await get_current_user_id(
                session=AsyncMock(),
                authorization='Bearer token',
            )


@pytest.mark.asyncio
async def test_get_current_user_id_raises_when_company_id_mismatch():
    user_id = uuid4()
    company_id = uuid4()
    other_company_id = uuid4()
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    mock_users_repo = MagicMock()
    mock_users_repo.get_user = AsyncMock(
        return_value=MagicMock(company_id=other_company_id)
    )

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={
                'sub': str(user_id),
                'typ': 'user',
                'company_id': str(company_id),
            },
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.UsersRepositoryPostgres',
            return_value=mock_users_repo,
        ),
    ):
        with pytest.raises(UnauthorizedException, match='Token inválido'):
            await get_current_user_id(
                session=AsyncMock(),
                authorization='Bearer token',
            )


@pytest.mark.asyncio
async def test_require_current_user_sets_request_state_user_and_company():
    user_id = uuid4()
    company_id = uuid4()
    request = Request({
        'type': 'http',
        'headers': [],
        'method': 'GET',
        'path': '/',
        'query_string': b'',
        'scheme': 'http',
        'server': ('test', 80),
        'client': ('test', 1234),
    })

    mock_users_repo = MagicMock()
    mock_users_repo.get_user = AsyncMock(return_value=MagicMock(company_id=company_id))
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={
                'sub': str(user_id),
                'typ': 'user',
                'company_id': str(company_id),
            },
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.UsersRepositoryPostgres',
            return_value=mock_users_repo,
        ),
    ):
        result = await require_current_user(
            request=request,
            session=AsyncMock(),
            authorization='Bearer token',
        )

    assert result == user_id
    assert request.state.user_id == user_id
    assert request.state.company_id == company_id


@pytest.mark.asyncio
async def test_require_current_user_raises_when_user_invalid():
    user_id = uuid4()
    company_id = uuid4()
    request = Request({
        'type': 'http',
        'headers': [],
        'method': 'GET',
        'path': '/',
        'query_string': b'',
        'scheme': 'http',
        'server': ('test', 80),
        'client': ('test', 1234),
    })

    mock_users_repo = MagicMock()
    mock_users_repo.get_user = AsyncMock(return_value=None)
    settings = MagicMock(JWT_SECRET='secret', JWT_ALGORITHM='HS256')

    with (
        patch(
            'src.interface.api.v1.dependencies.common.auth.get_settings',
            return_value=settings,
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.jwt.decode',
            return_value={
                'sub': str(user_id),
                'typ': 'user',
                'company_id': str(company_id),
            },
        ),
        patch(
            'src.interface.api.v1.dependencies.common.auth.UsersRepositoryPostgres',
            return_value=mock_users_repo,
        ),
    ):
        with pytest.raises(UnauthorizedException, match='User inválido'):
            await require_current_user(
                request=request,
                session=AsyncMock(),
                authorization='Bearer token',
            )
