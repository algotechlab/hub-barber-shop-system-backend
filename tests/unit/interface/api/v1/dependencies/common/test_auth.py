from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import jwt
import pytest
from src.domain.execptions.auth import UnauthorizedException
from src.interface.api.v1.dependencies.common.auth import (
    get_current_owner_id,
    require_current_owner,
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
            return_value={'sub': str(owner_id)},
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
            return_value={},
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
            return_value={'sub': 'not-a-uuid'},
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
            return_value={'sub': str(owner_id)},
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
