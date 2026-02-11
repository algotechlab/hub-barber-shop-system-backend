import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi import UploadFile
from src.domain.dtos.product import ProductDTO
from src.infrastructure.storage.s3 import UploadResult
from src.interface.api.v1.controller.product import ProductController
from src.interface.api.v1.schema.product import CreateProductSchema, UpdateProductSchema


@pytest.mark.unit
class TestProductController:
    @pytest.mark.asyncio
    async def test_list_products(self):
        company_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        use_case = AsyncMock()
        storage = AsyncMock()
        use_case.list_products.return_value = [
            ProductDTO(
                id=uuid.uuid4(),
                name='AAA',
                description='BBB',
                price=10,
                category='CCC',
                status=True,
                url_image='https://example.com/a.png',
                company_id=company_id,
                created_at=now,
                updated_at=now,
            )
        ]

        controller = ProductController(use_case, storage)
        result = await controller.list_products(company_id=company_id)

        assert len(result) == 1
        assert result[0].company_id == company_id

    @pytest.mark.asyncio
    async def test_create_product(self):
        company_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        use_case = AsyncMock()
        storage = AsyncMock()
        created = ProductDTO(
            id=uuid.uuid4(),
            name='AAA',
            description='BBB',
            price=10,
            category='CCC',
            status=True,
            url_image='https://example.com/a.png',
            company_id=company_id,
            created_at=now,
            updated_at=now,
        )
        use_case.create_product.return_value = created

        controller = ProductController(use_case, storage)
        payload = CreateProductSchema(
            name='AAA',
            description='BBB',
            price=10,
            category='CCC',
            status=True,
            url_image='https://example.com/a.png',
        )
        result = await controller.create_product(payload, company_id=company_id)

        assert result.company_id == company_id

    @pytest.mark.asyncio
    async def test_get_product(self):
        company_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        use_case = AsyncMock()
        storage = AsyncMock()
        product = ProductDTO(
            id=uuid.uuid4(),
            name='Produto',
            description='Desc',
            price=10,
            category='Cat',
            status=True,
            url_image='https://example.com/a.png',
            company_id=company_id,
            created_at=now,
            updated_at=now,
        )
        use_case.get_product.return_value = product

        controller = ProductController(use_case, storage)
        result = await controller.get_product(product.id, company_id=company_id)

        assert result.id == product.id

    @pytest.mark.asyncio
    async def test_update_product(self):
        company_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        use_case = AsyncMock()
        storage = AsyncMock()
        updated = ProductDTO(
            id=uuid.uuid4(),
            name='AAAA',
            description='BBB',
            price=10,
            category='CCC',
            status=True,
            url_image='https://example.com/a.png',
            company_id=company_id,
            created_at=now,
            updated_at=now,
        )
        use_case.update_product.return_value = updated

        controller = ProductController(use_case, storage)
        payload = UpdateProductSchema(name='AAAA')
        result = await controller.update_product(
            updated.id, payload, company_id=company_id
        )

        assert result.name == 'AAAA'

    @pytest.mark.asyncio
    async def test_delete_product(self):
        use_case = AsyncMock()
        storage = AsyncMock()
        use_case.delete_product.return_value = True

        controller = ProductController(use_case, storage)
        result = await controller.delete_product(uuid.uuid4(), company_id=uuid.uuid4())

        assert result is True

    @pytest.mark.asyncio
    async def test_upload_product_image(self):
        company_id = uuid.uuid4()
        use_case = AsyncMock()
        storage = AsyncMock()
        storage.upload_product_image.return_value = UploadResult(
            url='https://cdn.example.com/a.png',
            key='companies/x/products/y.png',
            content_type='image/png',
            size_bytes=3,
        )

        controller = ProductController(use_case, storage)
        file = AsyncMock(spec=UploadFile)
        result = await controller.upload_product_image(file=file, company_id=company_id)

        assert result.url == 'https://cdn.example.com/a.png'
