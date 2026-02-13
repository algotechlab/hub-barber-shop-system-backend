from uuid import UUID

from fastapi import UploadFile

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.product import CreateProductDTO, UpdateProductDTO
from src.domain.use_case.product import ProductUseCase
from src.infrastructure.storage.s3 import S3Storage
from src.interface.api.v1.schema.product import (
    CreateProductSchema,
    ProductOutSchema,
    ProductSchema,
    UpdateProductSchema,
    UploadProductImageOutSchema,
)


class ProductController:
    def __init__(self, product_use_case: ProductUseCase, storage: S3Storage):
        self.product_use_case = product_use_case
        self.storage = storage

    async def list_products(
        self, pagination: PaginationParamsDTO, company_id: UUID
    ) -> list[ProductSchema]:
        products = await self.product_use_case.list_products(pagination, company_id)
        return [ProductSchema(**product.model_dump()) for product in products]

    async def create_product(
        self,
        product: CreateProductSchema,
        company_id: UUID,
    ) -> ProductOutSchema:
        product_dto = CreateProductDTO(**product.model_dump(), company_id=company_id)
        created_product = await self.product_use_case.create_product(product_dto)
        return ProductOutSchema(**created_product.model_dump())

    async def get_product(self, id: UUID, company_id: UUID) -> ProductOutSchema:
        product = await self.product_use_case.get_product(id, company_id)
        return ProductOutSchema(**product.model_dump())

    async def update_product(
        self,
        id: UUID,
        product: UpdateProductSchema,
        company_id: UUID,
    ) -> ProductOutSchema:
        product_dto = UpdateProductDTO(**product.model_dump(exclude_unset=True))
        updated_product = await self.product_use_case.update_product(
            id, product_dto, company_id
        )
        return ProductOutSchema(**updated_product.model_dump())

    async def delete_product(self, id: UUID, company_id: UUID) -> bool:
        return await self.product_use_case.delete_product(id, company_id)

    async def upload_product_image(
        self, *, file: UploadFile, company_id: UUID
    ) -> UploadProductImageOutSchema:
        result = await self.storage.upload_product_image(
            file=file, company_id=company_id
        )
        return UploadProductImageOutSchema(url=result.url)
