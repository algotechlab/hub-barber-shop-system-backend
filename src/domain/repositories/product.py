from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.dtos.product import CreateProductDTO, ProductDTO, UpdateProductDTO


class ProductRepository(ABC):
    @abstractmethod
    async def create_product(self, product: CreateProductDTO) -> ProductDTO: ...

    @abstractmethod
    async def get_product(self, id: UUID, company_id: UUID) -> Optional[ProductDTO]: ...

    @abstractmethod
    async def list_products(self, company_id: UUID) -> List[ProductDTO]: ...

    @abstractmethod
    async def update_product(
        self, id: UUID, product: UpdateProductDTO, company_id: UUID
    ) -> Optional[ProductDTO]: ...

    @abstractmethod
    async def delete_product(self, id: UUID, company_id: UUID) -> bool: ...
