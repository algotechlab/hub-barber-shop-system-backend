import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from fastapi import Request
from src.interface.api.v1.controller.product import ProductController
from src.interface.api.v1.dependencies.common.auth import require_current_employee
from src.interface.api.v1.dependencies.product import get_product_controller
from src.interface.api.v1.schema.product import (
    CreateProductSchema,
    ProductOutSchema,
    ProductSchema,
    UpdateProductSchema,
    UploadProductImageOutSchema,
)
from src.main import app

URL_PRODUCTS = '/api/v1/products'
STATUS_CODE_200 = 200
STATUS_CODE_201 = 201
STATUS_CODE_204 = 204


def _install_overrides() -> AsyncMock:
    mock_controller = AsyncMock(spec=ProductController)

    def override_product_controller():
        return mock_controller

    app.dependency_overrides[get_product_controller] = override_product_controller

    async def override_require_current_employee(request: Request):
        request.state.company_id = uuid.uuid4()
        request.state.employee_id = uuid.uuid4()
        return request.state.employee_id

    app.dependency_overrides[require_current_employee] = (
        override_require_current_employee
    )
    return mock_controller


@pytest.fixture
def override_dependency_products():
    mock_controller = _install_overrides()
    yield mock_controller
    app.dependency_overrides.clear()


@pytest.mark.unit
class TestProductRoutes:
    def test_list_products_returns_200(self, client, override_dependency_products):
        product = ProductSchema(
            id=uuid.uuid4(),
            name='Produto',
            description='Desc',
            price=Decimal('10'),
            category='Cat',
            status=True,
            url_image='https://cdn.example.com/a.png',
            company_id=uuid.uuid4(),
        )
        override_dependency_products.list_products.return_value = [product]

        response = client.get(URL_PRODUCTS)

        assert response.status_code == STATUS_CODE_200, response.json()
        assert len(response.json()) == 1

    def test_create_product_returns_201(self, client, override_dependency_products):
        now = datetime.now(timezone.utc)
        product = ProductOutSchema(
            id=uuid.uuid4(),
            name='Produto',
            description='Desc',
            price=Decimal('10'),
            category='Cat',
            status=True,
            url_image='https://cdn.example.com/a.png',
            company_id=uuid.uuid4(),
            created_at=now,
            updated_at=now,
        )
        override_dependency_products.create_product.return_value = product

        payload = CreateProductSchema(
            name='Produto',
            description='Desc',
            price=Decimal('10'),
            category='Cat',
            status=True,
            url_image='https://cdn.example.com/a.png',
        ).model_dump(mode='json')

        response = client.post(URL_PRODUCTS, json=payload)

        assert response.status_code == STATUS_CODE_201, response.json()
        assert response.json()['name'] == 'Produto'

    def test_get_product_returns_200(self, client, override_dependency_products):
        now = datetime.now(timezone.utc)
        product = ProductOutSchema(
            id=uuid.uuid4(),
            name='Produto',
            description='Desc',
            price=Decimal('10'),
            category='Cat',
            status=True,
            url_image='https://cdn.example.com/a.png',
            company_id=uuid.uuid4(),
            created_at=now,
            updated_at=now,
        )
        override_dependency_products.get_product.return_value = product

        response = client.get(f'{URL_PRODUCTS}/{uuid.uuid4()}')

        assert response.status_code == STATUS_CODE_200, response.json()
        assert response.json()['id'] == str(product.id)

    def test_update_product_returns_200(self, client, override_dependency_products):
        now = datetime.now(timezone.utc)
        product = ProductOutSchema(
            id=uuid.uuid4(),
            name='Produto Novo',
            description='Desc',
            price=Decimal('10'),
            category='Cat',
            status=True,
            url_image='https://cdn.example.com/a.png',
            company_id=uuid.uuid4(),
            created_at=now,
            updated_at=now,
        )
        override_dependency_products.update_product.return_value = product

        payload = UpdateProductSchema(name='Produto Novo').model_dump(
            mode='json', exclude_none=True
        )
        response = client.patch(f'{URL_PRODUCTS}/{uuid.uuid4()}', json=payload)

        assert response.status_code == STATUS_CODE_200, response.json()
        assert response.json()['name'] == 'Produto Novo'

    def test_delete_product_returns_204(self, client, override_dependency_products):
        override_dependency_products.delete_product.return_value = True

        response = client.delete(f'{URL_PRODUCTS}/{uuid.uuid4()}')

        assert response.status_code == STATUS_CODE_204, response.json()

    def test_upload_product_image_returns_201(
        self, client, override_dependency_products
    ):
        override_dependency_products.upload_product_image.return_value = (
            UploadProductImageOutSchema(url='https://cdn.example.com/a.png')
        )

        response = client.post(
            f'{URL_PRODUCTS}/upload-image',
            files={'file': ('a.png', b'fake', 'image/png')},
        )

        assert response.status_code == STATUS_CODE_201, response.json()
        assert response.json()['url'] == 'https://cdn.example.com/a.png'
