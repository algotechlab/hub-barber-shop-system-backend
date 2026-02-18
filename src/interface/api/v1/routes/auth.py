from fastapi import APIRouter, status

from src.interface.api.v1.dependencies.auth import AuthControllerDep
from src.interface.api.v1.schema.auth import (
    EmployeeLoginSchema,
    OwnerLoginSchema,
    TokenOutSchema,
    TokenWithCompanyOutSchema,
    UserLoginSchema,
)

tags_metadata = {
    'name': 'Auth',
    'description': 'Autenticação e geração de tokens.',
}

router = APIRouter(
    prefix='/auth',
    tags=[tags_metadata['name']],
)


@router.post(
    '/login',
    status_code=status.HTTP_200_OK,
    response_model=TokenOutSchema,
    responses={
        status.HTTP_200_OK: {'description': 'Token gerado com sucesso'},
        status.HTTP_401_UNAUTHORIZED: {'description': 'Credenciais inválidas'},
    },
)
async def login_owner(
    controller: AuthControllerDep,
    credentials: OwnerLoginSchema,
) -> TokenOutSchema:
    return await controller.login_owner(credentials)


@router.post(
    '/login/employee',
    status_code=status.HTTP_200_OK,
    response_model=TokenWithCompanyOutSchema,
    responses={
        status.HTTP_200_OK: {'description': 'Token gerado com sucesso'},
        status.HTTP_401_UNAUTHORIZED: {'description': 'Credenciais inválidas'},
    },
)
async def login_employee(
    controller: AuthControllerDep,
    credentials: EmployeeLoginSchema,
) -> TokenWithCompanyOutSchema:
    return await controller.login_employee(credentials)


@router.post(
    '/login/user',
    status_code=status.HTTP_200_OK,
    response_model=TokenWithCompanyOutSchema,
    responses={
        status.HTTP_200_OK: {'description': 'Token gerado com sucesso'},
        status.HTTP_401_UNAUTHORIZED: {'description': 'Credenciais inválidas'},
    },
)
async def login_user(
    controller: AuthControllerDep,
    credentials: UserLoginSchema,
) -> TokenWithCompanyOutSchema:
    return await controller.login_user(credentials)
