from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.product import CreateProductDTO, ProductDTO, UpdateProductDTO
from src.domain.repositories.product import ProductRepository
from src.infrastructure.database.models.product import Product


class ProductRepositoryPostgres(ProductRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_product(self, product: CreateProductDTO) -> ProductDTO:
        try:
            product = Product(**product.model_dump())
            self.session.add(product)
            await self.session.commit()
            await self.session.refresh(product)
            return ProductDTO.model_validate(product)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_product(self, id: UUID, company_id: UUID) -> Optional[ProductDTO]:
        try:
            query = select(Product).where(
                Product.id.__eq__(id),
                Product.company_id.__eq__(company_id),
                Product.is_deleted.__eq__(False),
            )
            result = await self.session.execute(query)
            product = result.scalar_one_or_none()
            if product is None:
                return None
            return ProductDTO.model_validate(product)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def list_products(
        self, pagination: PaginationParamsDTO, company_id: UUID
    ) -> List[ProductDTO]:
        try:
            query = (
                select(Product)
                .where(
                    Product.company_id.__eq__(company_id),
                    Product.is_deleted.__eq__(False),
                )
                .order_by(Product.created_at.desc())
            )

            if pagination.filter_by and pagination.filter_value:
                query = query.filter(
                    getattr(Product, pagination.filter_by).ilike(
                        f'%{pagination.filter_value}%'
                    )
                )

            query = query.offset(pagination.offset).limit(pagination.limit)
            result = await self.session.execute(query)
            products = result.scalars().all()
            return [ProductDTO.model_validate(product) for product in products]
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def update_product(
        self, id: UUID, product: UpdateProductDTO, company_id: UUID
    ) -> Optional[ProductDTO]:
        try:
            update_data = product.model_dump(exclude_unset=True, exclude_none=True)
            stmt = (
                update(Product)
                .where(
                    Product.id.__eq__(id),
                    Product.company_id.__eq__(company_id),
                    Product.is_deleted.__eq__(False),
                )
                .values(**update_data)
                .returning(Product)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            updated_product = result.scalar_one_or_none()
            if updated_product is None:
                return None
            return ProductDTO.model_validate(updated_product)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def delete_product(self, id: UUID, company_id: UUID) -> bool:
        try:
            stmt = (
                update(Product)
                .where(
                    Product.id.__eq__(id),
                    Product.company_id.__eq__(company_id),
                    Product.is_deleted.__eq__(False),
                )
                .values(is_deleted=True)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
