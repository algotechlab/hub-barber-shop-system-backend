from typing import List
from uuid import UUID

from fastapi import APIRouter, status

from src.interface.api.v1.dependencies.common.pagination import PaginationParamsDep
from src.interface.api.v1.dependencies.users import UsersRepositoryDep
from src.interface.api.v1.schema.users import (
    CreateUserSchema,
    UpdateUserSchema,
    UserOutSchema,
)

tags_metadata = {
    'name': 'Usuários',
    'description': ('Modulo de usuários.'),
}


router = APIRouter(
    prefix='/users',
    tags=[tags_metadata['name']],
)


@router.post(
    '',
    description='Rota para adicionar usuário',
    status_code=status.HTTP_201_CREATED,
    response_model=UserOutSchema,
    responses={
        status.HTTP_201_CREATED: {
            'description': 'Usuário criado com sucesso',
        },
        status.HTTP_409_CONFLICT: {
            'description': 'Usuário com email duplicado',
        },
    },
)
async def add_users(
    controller: UsersRepositoryDep,
    users: CreateUserSchema,
) -> UserOutSchema:
    return await controller.create_user(users)


@router.get('', description='Rota para listar usuários', status_code=status.HTTP_200_OK)
async def list_users(
    controller: UsersRepositoryDep, pagination: PaginationParamsDep
) -> List[UserOutSchema]:
    return await controller.list_users(pagination)


@router.patch(
    '/{user_id}',
    description='Rota para atualizar usuário',
    status_code=status.HTTP_200_OK,
    response_model=UserOutSchema,
    responses={
        status.HTTP_200_OK: {
            'description': 'Usuário atualizado com sucesso',
        },
        status.HTTP_404_NOT_FOUND: {
            'description': 'Usuário não encontrado',
        },
    },
)
async def update_user(
    controller: UsersRepositoryDep,
    user_id: UUID,
    users: UpdateUserSchema,
) -> UserOutSchema:
    return await controller.update_user(user_id, users)


@router.delete(
    '/{user_id}',
    description='Rota para deletar usuário',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(controller: UsersRepositoryDep, user_id: UUID) -> None:
    return await controller.delete_user(user_id)
