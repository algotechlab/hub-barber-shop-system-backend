from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.product import CreateProductDTO, ProductDTO, UpdateProductDTO
from src.domain.service.product import ProductService

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_product_delegates_to_repository():
    repo = AsyncMock()
    service = ProductService(repo)
    dto = CreateProductDTO(
        name='Produto',
        description='Desc',
        price=Decimal('10'),
        category='Cat',
        status=True,
        url_image='https://example.com/a.png',
        company_id=uuid4(),
    )
    now = datetime.now(timezone.utc)
    repo.create_product.return_value = ProductDTO(
        id=uuid4(),
        name=dto.name,
        description=dto.description,
        price=dto.price,
        category=dto.category,
        status=dto.status,
        url_image=dto.url_image,
        company_id=dto.company_id,
        created_at=now,
        updated_at=now,
    )

    result = await service.create_product(dto)

    repo.create_product.assert_awaited_once_with(dto)
    assert result.company_id == dto.company_id


@pytest.mark.asyncio
async def test_list_products_delegates_to_repository():
    repo = AsyncMock()
    service = ProductService(repo)
    company_id = uuid4()
    repo.list_products.return_value = []

    pagination = PaginationParamsDTO()
    result = await service.list_products(pagination, company_id)

    repo.list_products.assert_awaited_once_with(pagination, company_id)
    assert result == []


@pytest.mark.asyncio
async def test_get_product_delegates_to_repository():
    repo = AsyncMock()
    service = ProductService(repo)
    product_id = uuid4()
    company_id = uuid4()
    repo.get_product.return_value = None

    result = await service.get_product(product_id, company_id)

    repo.get_product.assert_awaited_once_with(product_id, company_id)
    assert result is None


@pytest.mark.asyncio
async def test_update_product_delegates_to_repository():
    repo = AsyncMock()
    service = ProductService(repo)
    product_id = uuid4()
    company_id = uuid4()
    dto = UpdateProductDTO(name='Novo Nome')
    repo.update_product.return_value = None

    result = await service.update_product(product_id, dto, company_id)

    repo.update_product.assert_awaited_once_with(product_id, dto, company_id)
    assert result is None


@pytest.mark.asyncio
async def test_delete_product_delegates_to_repository():
    repo = AsyncMock()
    service = ProductService(repo)
    product_id = uuid4()
    company_id = uuid4()
    repo.delete_product.return_value = True

    result = await service.delete_product(product_id, company_id)

    repo.delete_product.assert_awaited_once_with(product_id, company_id)
    assert result is True
