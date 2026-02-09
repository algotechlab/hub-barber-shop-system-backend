from typing import List
from uuid import UUID

from fastapi import APIRouter, status

from src.interface.api.v1.dependencies.common.pagination import PaginationParamsDep
from src.interface.api.v1.dependencies.owner import OwnerControllerDep
from src.interface.api.v1.schema.owner import (
    CreateOwnerSchema,
    OwnerOutSchema,
    UpdateOwnerSchema,
)

tags_metadata = {
    'name': 'Proprietários',
    'description': ('Modulo de proprietários.'),
}


router = APIRouter(
    prefix='/owners',
    tags=[tags_metadata['name']],
)


@router.post(
    '/',
    response_model=OwnerOutSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            'description': 'Proprietário criado com sucesso',
        },
    },
)
async def create_owner(owner: CreateOwnerSchema, controller: OwnerControllerDep):
    return await controller.create_owner(owner)


@router.get(
    '/{owner_id}',
    response_model=OwnerOutSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            'description': 'Proprietário recuperado com sucesso',
        },
    },
)
async def get_owner(owner_id: UUID, controller: OwnerControllerDep):
    return await controller.get_owner(owner_id)


@router.get(
    '',
    response_model=List[OwnerOutSchema],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            'description': 'Proprietários recuperados com sucesso',
        },
    },
)
async def list_owners(
    controller: OwnerControllerDep,
    pagination: PaginationParamsDep,
) -> List[OwnerOutSchema]:
    return await controller.list_owners(pagination)


@router.patch(
    '/{owner_id}',
    response_model=OwnerOutSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            'description': 'Proprietário atualizado com sucesso',
        },
    },
)
async def update_owner(
    owner_id: UUID, owner: UpdateOwnerSchema, controller: OwnerControllerDep
):
    return await controller.update_owner(owner_id, owner)


@router.delete(
    '/{owner_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_owner(owner_id: UUID, controller: OwnerControllerDep):
    return await controller.delete_owner(owner_id)
