from typing import Annotated

from fastapi import Depends

from src.domain.service.product import ProductService
from src.domain.use_case.product import ProductUseCase
from src.infrastructure.repositories.product_postgres import ProductRepositoryPostgres
from src.infrastructure.storage.s3 import S3Storage
from src.interface.api.v1.controller.product import ProductController
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep


async def get_product_controller(session: VerifiedSessionDep) -> ProductController:
    """
    Singleton para o controller de produtos.
    """
    product_repository = ProductRepositoryPostgres(session)
    product_service = ProductService(product_repository)
    product_use_case = ProductUseCase(product_service)
    storage = S3Storage.from_settings()
    return ProductController(product_use_case, storage)


ProductRepositoryDep = Annotated[ProductController, Depends(get_product_controller)]
