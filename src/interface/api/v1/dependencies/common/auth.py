from typing import Annotated, Optional
from uuid import UUID

import jwt
from fastapi import Depends, Header

from src.core.config.settings import get_settings
from src.domain.execptions.auth import UnauthorizedException
from src.infrastructure.repositories.owner_postgres import OwnerRepositoryPostgres
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep

AuthorizationHeaderDep = Annotated[
    Optional[str],
    Header(
        alias='Authorization',
        description='Bearer <access_token>',
    ),
]


EQUALS_TO_BEARER = 'bearer'
RESULT_LENGTH = 2


async def get_current_owner_id(
    session: VerifiedSessionDep,
    authorization: AuthorizationHeaderDep,
) -> UUID:
    if not authorization:
        raise UnauthorizedException('Token ausente')

    parts = authorization.split()
    if len(parts) != RESULT_LENGTH or parts[0].lower() != EQUALS_TO_BEARER:
        raise UnauthorizedException('Header Authorization inválido')

    token = parts[1]
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.exceptions.PyJWTError as error:
        raise UnauthorizedException('Token inválido') from error

    sub = payload.get('sub')
    if not sub:
        raise UnauthorizedException('Token inválido')

    try:
        owner_id = UUID(str(sub))
    except ValueError as error:
        raise UnauthorizedException('Token inválido') from error

    owner_repo = OwnerRepositoryPostgres(session)
    owner = await owner_repo.get_owner(owner_id)
    if owner is None:
        raise UnauthorizedException('Owner inválido')

    return owner_id


CurrentOwnerIdDep = Annotated[UUID, Depends(get_current_owner_id)]
