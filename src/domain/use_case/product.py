from typing import List
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.product import CreateProductDTO, ProductDTO, UpdateProductDTO
from src.domain.execptions.product import ProductNotFoundException
from src.domain.service.product import ProductService


class ProductUseCase:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    async def create_product(self, product: CreateProductDTO) -> ProductDTO:
        return await self.product_service.create_product(product)

    async def get_product(self, id: UUID, company_id: UUID) -> ProductDTO:
        product = await self.product_service.get_product(id, company_id)
        if product is None:
            raise ProductNotFoundException('Produto não encontrado')
        return product

    async def list_products(
        self, pagination: PaginationParamsDTO, company_id: UUID
    ) -> List[ProductDTO]:
        return await self.product_service.list_products(pagination, company_id)

    async def update_product(
        self, id: UUID, product: UpdateProductDTO, company_id: UUID
    ) -> ProductDTO:
        updated_product = await self.product_service.update_product(
            id, product, company_id
        )
        if updated_product is None:
            raise ProductNotFoundException('Produto não encontrado')
        return updated_product

    async def delete_product(self, id: UUID, company_id: UUID) -> bool:
        deleted = await self.product_service.delete_product(id, company_id)
        if not deleted:
            raise ProductNotFoundException('Produto não encontrado')
        return deleted
