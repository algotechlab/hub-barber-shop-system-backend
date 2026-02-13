from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, Request, UploadFile, status

from src.interface.api.v1.dependencies.common.auth import require_current_employee
from src.interface.api.v1.dependencies.common.pagination import PaginationParamsDep
from src.interface.api.v1.dependencies.service import ServiceRepositoryDep
from src.interface.api.v1.schema.service import (
    CreateServiceSchema,
    ServiceSchema,
    UpdateServiceSchema,
    UploadServiceImageOutSchema,
)

tags_metadata = {
    'name': 'Serviços',
    'description': ('Modulo de serviços.'),
}

router = APIRouter(
    prefix='/services',
    tags=[tags_metadata['name']],
    dependencies=[Depends(require_current_employee)],
)


@router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    response_model=ServiceSchema,
    responses={
        status.HTTP_201_CREATED: {
            'description': 'Serviço criado com sucesso',
        },
    },
)
async def create_service(
    controller: ServiceRepositoryDep, service: CreateServiceSchema, request: Request
) -> ServiceSchema:
    return await controller.create_service(service, company_id=request.state.company_id)


@router.get(
    '',
    status_code=status.HTTP_200_OK,
    response_model=List[ServiceSchema],
    responses={
        status.HTTP_200_OK: {
            'description': 'Serviços listados com sucesso',
        },
    },
)
async def list_services(
    controller: ServiceRepositoryDep, request: Request, pagination: PaginationParamsDep
) -> List[ServiceSchema]:
    return await controller.list_services(
        pagination, company_id=request.state.company_id
    )


@router.get(
    '/{service_id}',
    status_code=status.HTTP_200_OK,
    response_model=ServiceSchema,
    responses={
        status.HTTP_200_OK: {
            'description': 'Serviço encontrado com sucesso',
        },
    },
)
async def get_service(
    controller: ServiceRepositoryDep, service_id: UUID, request: Request
) -> ServiceSchema:
    return await controller.get_service(service_id, company_id=request.state.company_id)


@router.patch(
    '/{service_id}',
    status_code=status.HTTP_200_OK,
    response_model=ServiceSchema,
    responses={
        status.HTTP_200_OK: {
            'description': 'Serviço atualizado com sucesso',
        },
    },
)
async def update_service(
    controller: ServiceRepositoryDep,
    service_id: UUID,
    service: UpdateServiceSchema,
    request: Request,
) -> ServiceSchema:
    return await controller.update_service(
        service_id, service, company_id=request.state.company_id
    )


@router.delete(
    '/{service_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            'description': 'Serviço deletado com sucesso',
        },
    },
)
async def delete_service(
    controller: ServiceRepositoryDep, service_id: UUID, request: Request
) -> None:
    await controller.delete_service(service_id, company_id=request.state.company_id)


@router.post(
    '/upload-image',
    description='Rota para enviar imagem do serviço para o S3',
    status_code=status.HTTP_201_CREATED,
    response_model=UploadServiceImageOutSchema,
)
async def upload_service_image(
    controller: ServiceRepositoryDep,
    request: Request,
    file: UploadFile = File(...),
) -> UploadServiceImageOutSchema:
    return await controller.upload_service_image(
        file=file, company_id=request.state.company_id
    )
