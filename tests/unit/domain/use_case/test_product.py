from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.product import CreateProductDTO, ProductDTO, UpdateProductDTO
from src.domain.execptions.product import ProductNotFoundException
from src.domain.use_case.product import ProductUseCase

pytestmark = pytest.mark.unit


def _product(company_id):
    now = datetime.now(timezone.utc)
    return ProductDTO(
        id=uuid4(),
        name='Produto',
        description='Desc',
        price=Decimal('10'),
        category='Cat',
        status=True,
        url_image='https://example.com/a.png',
        company_id=company_id,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_create_product_delegates_to_service():
    service = AsyncMock()
    use_case = ProductUseCase(service)
    company_id = uuid4()
    dto = CreateProductDTO(
        name='Produto',
        description='Desc',
        price=Decimal('10'),
        category='Cat',
        status=True,
        url_image='https://example.com/a.png',
        company_id=company_id,
    )
    expected = _product(company_id)
    service.create_product.return_value = expected

    result = await use_case.create_product(dto)

    service.create_product.assert_awaited_once_with(dto)
    assert result == expected


@pytest.mark.asyncio
async def test_get_product_raises_when_not_found():
    service = AsyncMock()
    service.get_product.return_value = None
    use_case = ProductUseCase(service)

    with pytest.raises(ProductNotFoundException):
        await use_case.get_product(uuid4(), uuid4())


@pytest.mark.asyncio
async def test_get_product_returns_when_found():
    service = AsyncMock()
    company_id = uuid4()
    expected = _product(company_id)
    service.get_product.return_value = expected
    use_case = ProductUseCase(service)

    result = await use_case.get_product(expected.id, company_id)

    assert result == expected


@pytest.mark.asyncio
async def test_list_products_delegates_to_service():
    service = AsyncMock()
    service.list_products.return_value = []
    use_case = ProductUseCase(service)
    company_id = uuid4()

    pagination = PaginationParamsDTO()
    result = await use_case.list_products(pagination, company_id)

    service.list_products.assert_awaited_once_with(pagination, company_id)
    assert result == []


@pytest.mark.asyncio
async def test_update_product_raises_when_not_found():
    service = AsyncMock()
    service.update_product.return_value = None
    use_case = ProductUseCase(service)

    with pytest.raises(ProductNotFoundException):
        await use_case.update_product(uuid4(), UpdateProductDTO(name='X'), uuid4())


@pytest.mark.asyncio
async def test_update_product_returns_when_found():
    service = AsyncMock()
    company_id = uuid4()
    expected = _product(company_id)
    service.update_product.return_value = expected
    use_case = ProductUseCase(service)

    result = await use_case.update_product(
        expected.id, UpdateProductDTO(name='X'), company_id
    )

    assert result == expected


@pytest.mark.asyncio
async def test_delete_product_raises_when_not_deleted():
    service = AsyncMock()
    service.delete_product.return_value = False
    use_case = ProductUseCase(service)

    with pytest.raises(ProductNotFoundException):
        await use_case.delete_product(uuid4(), uuid4())


@pytest.mark.asyncio
async def test_delete_product_returns_true_when_deleted():
    service = AsyncMock()
    service.delete_product.return_value = True
    use_case = ProductUseCase(service)

    result = await use_case.delete_product(uuid4(), uuid4())

    assert result is True
