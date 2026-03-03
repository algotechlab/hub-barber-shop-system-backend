from uuid import UUID

from fastapi import APIRouter, Depends, File, Request, UploadFile, status

from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee_or_user,
)
from src.interface.api.v1.dependencies.common.pagination import PaginationParamsDep
from src.interface.api.v1.dependencies.product import ProductRepositoryDep
from src.interface.api.v1.schema.product import (
    CreateProductSchema,
    ProductOutSchema,
    ProductSchema,
    UpdateProductSchema,
    UploadProductImageOutSchema,
)

tags_metadata = {
    'name': 'Produtos',
    'description': ('Modulo de produtos.'),
}

router = APIRouter(
    prefix='/products',
    tags=[tags_metadata['name']],
    dependencies=[Depends(require_current_employee_or_user)],
)


@router.get('', description='Rota para listar produtos', status_code=status.HTTP_200_OK)
async def list_products(
    controller: ProductRepositoryDep, request: Request, pagination: PaginationParamsDep
) -> list[ProductSchema]:
    return await controller.list_products(
        pagination, company_id=request.state.company_id
    )


@router.post(
    '',
    description='Rota para criar produto',
    status_code=status.HTTP_201_CREATED,
    response_model=ProductOutSchema,
)
async def create_product(
    controller: ProductRepositoryDep, product: CreateProductSchema, request: Request
) -> ProductOutSchema:
    return await controller.create_product(product, company_id=request.state.company_id)


@router.post(
    '/upload-image',
    description='Rota para enviar imagem do produto para o S3',
    status_code=status.HTTP_201_CREATED,
    response_model=UploadProductImageOutSchema,
)
async def upload_product_image(
    controller: ProductRepositoryDep,
    request: Request,
    file: UploadFile = File(...),
) -> UploadProductImageOutSchema:
    return await controller.upload_product_image(
        file=file, company_id=request.state.company_id
    )


@router.get(
    '/{product_id}',
    description='Rota para buscar produto',
    status_code=status.HTTP_200_OK,
    response_model=ProductOutSchema,
)
async def get_product(
    controller: ProductRepositoryDep, product_id: UUID, request: Request
) -> ProductOutSchema:
    return await controller.get_product(product_id, company_id=request.state.company_id)


@router.patch(
    '/{product_id}',
    description='Rota para atualizar produto',
    status_code=status.HTTP_200_OK,
    response_model=ProductOutSchema,
)
async def update_product(
    controller: ProductRepositoryDep,
    product_id: UUID,
    product: UpdateProductSchema,
    request: Request,
) -> ProductOutSchema:
    return await controller.update_product(
        product_id, product, company_id=request.state.company_id
    )


@router.delete(
    '/{product_id}',
    description='Rota para deletar produto',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    controller: ProductRepositoryDep, product_id: UUID, request: Request
) -> None:
    await controller.delete_product(product_id, company_id=request.state.company_id)
