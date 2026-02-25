from typing import Annotated, Optional
from uuid import UUID

import jwt
from fastapi import Depends, Header, Request

from src.core.config.settings import get_settings
from src.domain.exceptions.auth import UnauthorizedException
from src.infrastructure.repositories.employee_postgres import EmployeeRepositoryPostgres
from src.infrastructure.repositories.owner_postgres import OwnerRepositoryPostgres
from src.infrastructure.repositories.users_postgres import UsersRepositoryPostgres
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
TOKEN_TYPE_OWNER = 'owner'
TOKEN_TYPE_EMPLOYEE = 'employee'
TOKEN_TYPE_USER = 'user'


def _parse_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise UnauthorizedException('Token ausente')

    parts = authorization.split()
    if len(parts) != RESULT_LENGTH or parts[0].lower() != EQUALS_TO_BEARER:
        raise UnauthorizedException('Header Authorization inválido')

    return parts[1]


def _decode_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.exceptions.PyJWTError as error:
        raise UnauthorizedException('Token inválido') from error


def _get_uuid_claim(payload: dict, key: str) -> UUID:
    value = payload.get(key)
    if not value:
        raise UnauthorizedException('Token inválido')
    try:
        return UUID(str(value))
    except ValueError as error:
        raise UnauthorizedException('Token inválido') from error


def _require_token_type(payload: dict, expected: str) -> None:
    if payload.get('typ') != expected:
        raise UnauthorizedException('Token inválido')


async def get_current_owner_id(
    session: VerifiedSessionDep,
    authorization: AuthorizationHeaderDep,
) -> UUID:
    token = _parse_bearer_token(authorization)
    payload = _decode_token(token)
    _require_token_type(payload, TOKEN_TYPE_OWNER)
    owner_id = _get_uuid_claim(payload, 'sub')

    owner_repo = OwnerRepositoryPostgres(session)
    owner = await owner_repo.get_owner(owner_id)
    if owner is None:
        raise UnauthorizedException('Owner inválido')

    return owner_id


async def get_current_employee_id(
    session: VerifiedSessionDep,
    authorization: AuthorizationHeaderDep,
) -> UUID:
    token = _parse_bearer_token(authorization)
    payload = _decode_token(token)
    _require_token_type(payload, TOKEN_TYPE_EMPLOYEE)

    employee_id = _get_uuid_claim(payload, 'sub')
    company_id = _get_uuid_claim(payload, 'company_id')

    employee_repo = EmployeeRepositoryPostgres(session)
    employee = await employee_repo.get_employee(employee_id, company_id=company_id)
    if employee is None:
        raise UnauthorizedException('Employee inválido')

    return employee_id


async def get_current_user_id(
    session: VerifiedSessionDep,
    authorization: AuthorizationHeaderDep,
) -> UUID:
    token = _parse_bearer_token(authorization)
    payload = _decode_token(token)
    _require_token_type(payload, TOKEN_TYPE_USER)

    user_id = _get_uuid_claim(payload, 'sub')
    company_id = _get_uuid_claim(payload, 'company_id')

    users_repo = UsersRepositoryPostgres(session)
    user = await users_repo.get_user(user_id)
    if user is None:
        raise UnauthorizedException('User inválido')
    if user.company_id != company_id:
        raise UnauthorizedException('Token inválido')

    return user_id


async def require_current_owner(
    request: Request,
    session: VerifiedSessionDep,
    authorization: AuthorizationHeaderDep,
) -> UUID:
    """
    Valida o Bearer token e salva o
    owner_id em request.state.owner_id.

    Útil para proteger um router inteiro
    Com dependencies=[Depends(require_current_owner)].
    """
    owner_id = await get_current_owner_id(session=session, authorization=authorization)
    request.state.owner_id = owner_id
    return owner_id


async def require_current_employee(
    request: Request,
    session: VerifiedSessionDep,
    authorization: AuthorizationHeaderDep,
) -> UUID:
    """
    Valida o Bearer token de employee e salva no request.state:
    - employee_id
    - company_id
    """
    token = _parse_bearer_token(authorization)
    payload = _decode_token(token)
    _require_token_type(payload, TOKEN_TYPE_EMPLOYEE)

    employee_id = _get_uuid_claim(payload, 'sub')
    company_id = _get_uuid_claim(payload, 'company_id')

    employee_repo = EmployeeRepositoryPostgres(session)
    employee = await employee_repo.get_employee(employee_id, company_id=company_id)
    if employee is None:
        raise UnauthorizedException('Employee inválido')

    request.state.employee_id = employee_id
    request.state.company_id = company_id
    return employee_id


async def require_current_user(
    request: Request,
    session: VerifiedSessionDep,
    authorization: AuthorizationHeaderDep,
) -> UUID:
    """
    Valida o Bearer token de user e salva no request.state:
    - user_id
    - company_id
    """
    token = _parse_bearer_token(authorization)
    payload = _decode_token(token)
    _require_token_type(payload, TOKEN_TYPE_USER)

    user_id = _get_uuid_claim(payload, 'sub')
    company_id = _get_uuid_claim(payload, 'company_id')

    users_repo = UsersRepositoryPostgres(session)
    user = await users_repo.get_user(user_id)
    if user is None or user.company_id != company_id:
        raise UnauthorizedException('User inválido')

    request.state.user_id = user_id
    request.state.company_id = company_id
    return user_id


async def require_current_employee_or_user(
    request: Request,
    session: VerifiedSessionDep,
    authorization: AuthorizationHeaderDep,
) -> UUID:
    """
    Valida o Bearer token e aceita typ:
    - employee: salva employee_id + company_id
    - user: salva user_id + company_id

    Útil para proteger um router inteiro quando
    a rota pode ser acessada por employee OU user.
    """
    token = _parse_bearer_token(authorization)
    payload = _decode_token(token)

    token_type = payload.get('typ')
    if token_type == TOKEN_TYPE_EMPLOYEE:
        employee_id = _get_uuid_claim(payload, 'sub')
        company_id = _get_uuid_claim(payload, 'company_id')

        employee_repo = EmployeeRepositoryPostgres(session)
        employee = await employee_repo.get_employee(employee_id, company_id=company_id)
        if employee is None:
            raise UnauthorizedException('Employee inválido')

        request.state.employee_id = employee_id
        request.state.company_id = company_id
        return employee_id

    if token_type == TOKEN_TYPE_USER:
        user_id = _get_uuid_claim(payload, 'sub')
        company_id = _get_uuid_claim(payload, 'company_id')

        users_repo = UsersRepositoryPostgres(session)
        user = await users_repo.get_user(user_id)
        if user is None or user.company_id != company_id:
            raise UnauthorizedException('User inválido')

        request.state.user_id = user_id
        request.state.company_id = company_id
        return user_id

    raise UnauthorizedException('Token inválido')


async def require_current_employee_or_owner(
    request: Request,
    session: VerifiedSessionDep,
    authorization: AuthorizationHeaderDep,
) -> UUID:
    """
    Valida o Bearer token e aceita typ:
    - employee: salva employee_id + company_id
    - owner: salva owner_id
    """
    token = _parse_bearer_token(authorization)
    payload = _decode_token(token)

    token_type = payload.get('typ')
    if token_type == TOKEN_TYPE_EMPLOYEE:
        return await require_current_employee(
            request=request, session=session, authorization=authorization
        )
    if token_type == TOKEN_TYPE_OWNER:
        return await require_current_owner(
            request=request, session=session, authorization=authorization
        )
    raise UnauthorizedException('Token inválido')


CurrentOwnerIdDep = Annotated[UUID, Depends(get_current_owner_id)]
CurrentEmployeeIdDep = Annotated[UUID, Depends(get_current_employee_id)]
CurrentUserIdDep = Annotated[UUID, Depends(get_current_user_id)]
CurrentEmployeeOrOwnerIdDep = Annotated[
    UUID, Depends(require_current_employee_or_owner)
]
