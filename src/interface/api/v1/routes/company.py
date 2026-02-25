from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee_or_owner,
    require_current_owner,
)
from src.interface.api.v1.dependencies.common.pagination import PaginationParamsDep
from src.interface.api.v1.dependencies.company import CompanyRepositoryDep
from src.interface.api.v1.schema.company import CompanyOutSchema, CreateCompanySchema

tags_metadata = {
    'name': 'Companias',
    'description': ('Modulo de companias.'),
}


router = APIRouter(
    prefix='/company',
    tags=[tags_metadata['name']],
)


@router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    response_model=CompanyOutSchema,
    dependencies=[Depends(require_current_owner)],
    responses={
        status.HTTP_201_CREATED: {
            'description': 'Compania criada com sucesso',
        },
        status.HTTP_409_CONFLICT: {
            'description': 'Compania com slug duplicado',
        },
    },
)
async def create_company(
    controller: CompanyRepositoryDep,
    company: CreateCompanySchema,
    request: Request,
) -> CompanyOutSchema:
    return await controller.create_company(company, owner_id=request.state.owner_id)


@router.get(
    '/{company_id}',
    status_code=status.HTTP_200_OK,
    response_model=CompanyOutSchema,
    dependencies=[Depends(require_current_employee_or_owner)],
)
async def get_company(
    controller: CompanyRepositoryDep, company_id: UUID
) -> CompanyOutSchema:
    return await controller.get_company(company_id)


@router.get(
    '',
    status_code=status.HTTP_200_OK,
    response_model=List[CompanyOutSchema],
    dependencies=[Depends(require_current_employee_or_owner)],
    responses={
        status.HTTP_200_OK: {
            'description': 'Companias listadas com sucesso',
        },
    },
)
async def list_companies(
    controller: CompanyRepositoryDep, pagination: PaginationParamsDep
) -> List[CompanyOutSchema]:
    return await controller.list_companies(pagination)


@router.delete(
    '/{company_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_current_owner)],
    responses={
        status.HTTP_204_NO_CONTENT: {
            'description': 'Compania deletada com sucesso',
        },
    },
)
async def delete_company(controller: CompanyRepositoryDep, company_id: UUID) -> None:
    return await controller.delete_company(company_id)
