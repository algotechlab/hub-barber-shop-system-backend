from typing import List, Optional
from uuid import UUID

from src.domain.dtos.product import CreateProductDTO, ProductDTO, UpdateProductDTO
from src.domain.repositories.product import ProductRepository


class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    async def create_product(self, product: CreateProductDTO) -> ProductDTO:
        return await self.product_repository.create_product(product)

    async def list_products(self, company_id: UUID) -> List[ProductDTO]:
        return await self.product_repository.list_products(company_id)

    async def get_product(self, id: UUID, company_id: UUID) -> Optional[ProductDTO]:
        return await self.product_repository.get_product(id, company_id)

    async def update_product(
        self, id: UUID, product: UpdateProductDTO, company_id: UUID
    ) -> Optional[ProductDTO]:
        return await self.product_repository.update_product(id, product, company_id)

    async def delete_product(self, id: UUID, company_id: UUID) -> bool:
        return await self.product_repository.delete_product(id, company_id)
