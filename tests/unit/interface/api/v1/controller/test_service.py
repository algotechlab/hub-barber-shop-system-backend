import uuid
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from fastapi import UploadFile
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.service import ServiceDTO
from src.infrastructure.storage.s3 import UploadResult
from src.interface.api.v1.controller.service import ServiceController
from src.interface.api.v1.schema.service import CreateServiceSchema, UpdateServiceSchema


@pytest.mark.unit
class TestServiceController:
    @pytest.mark.asyncio
    async def test_list_services(self):
        company_id = uuid.uuid4()
        use_case = AsyncMock()
        storage = AsyncMock()
        use_case.list_services.return_value = [
            ServiceDTO(
                id=uuid.uuid4(),
                name='Corte',
                description='Desc',
                price=Decimal('10'),
                duration=30,
                category='Cat',
                time_to_spend=30,
                status=True,
                url_image='https://cdn.example.com/a.png',
                company_id=company_id,
            )
        ]

        controller = ServiceController(use_case, storage)
        pagination = PaginationParamsDTO()
        result = await controller.list_services(pagination, company_id=company_id)

        assert len(result) == 1
        assert result[0].name == 'Corte'
        use_case.list_services.assert_awaited_once_with(pagination, company_id)

    @pytest.mark.asyncio
    async def test_create_service(self):
        company_id = uuid.uuid4()
        use_case = AsyncMock()
        storage = AsyncMock()
        created = ServiceDTO(
            id=uuid.uuid4(),
            name='Corte',
            description='Desc',
            price=Decimal('10'),
            duration=30,
            category='Cat',
            time_to_spend=30,
            status=True,
            url_image='https://cdn.example.com/a.png',
            company_id=company_id,
        )
        use_case.create_service.return_value = created

        controller = ServiceController(use_case, storage)
        payload = CreateServiceSchema(
            name='Corte',
            description='Desc',
            price=10.0,
            duration=30,
            category='Cat',
            time_to_spend=30,
            status=True,
            url_image='https://cdn.example.com/a.png',
        )
        result = await controller.create_service(payload, company_id=company_id)

        assert result.id == created.id
        assert result.name == 'Corte'

    @pytest.mark.asyncio
    async def test_get_service(self):
        company_id = uuid.uuid4()
        use_case = AsyncMock()
        storage = AsyncMock()
        service = ServiceDTO(
            id=uuid.uuid4(),
            name='Corte',
            description='Desc',
            price=Decimal('10'),
            duration=30,
            category='Cat',
            time_to_spend=30,
            status=True,
            url_image='https://cdn.example.com/a.png',
            company_id=company_id,
        )
        use_case.get_service.return_value = service

        controller = ServiceController(use_case, storage)
        result = await controller.get_service(service.id, company_id=company_id)

        assert result.id == service.id

    @pytest.mark.asyncio
    async def test_update_service(self):
        company_id = uuid.uuid4()
        use_case = AsyncMock()
        storage = AsyncMock()
        updated = ServiceDTO(
            id=uuid.uuid4(),
            name='Corte Novo',
            description='Desc',
            price=Decimal('10'),
            duration=30,
            category='Cat',
            time_to_spend=30,
            status=True,
            url_image='https://cdn.example.com/a.png',
            company_id=company_id,
        )
        use_case.update_service.return_value = updated

        controller = ServiceController(use_case, storage)
        payload = UpdateServiceSchema(name='Corte Novo')
        result = await controller.update_service(
            updated.id, payload, company_id=company_id
        )

        assert result.name == 'Corte Novo'

    @pytest.mark.asyncio
    async def test_delete_service(self):
        use_case = AsyncMock()
        storage = AsyncMock()
        use_case.delete_service.return_value = True

        controller = ServiceController(use_case, storage)
        result = await controller.delete_service(uuid.uuid4(), company_id=uuid.uuid4())

        assert result is True

    @pytest.mark.asyncio
    async def test_upload_service_image(self):
        company_id = uuid.uuid4()
        use_case = AsyncMock()
        storage = AsyncMock()
        storage.upload_service_image.return_value = UploadResult(
            url='https://cdn.example.com/a.png',
            key='companies/x/services/y.png',
            content_type='image/png',
            size_bytes=3,
        )

        controller = ServiceController(use_case, storage)
        file = AsyncMock(spec=UploadFile)
        result = await controller.upload_service_image(file=file, company_id=company_id)

        assert result.url == 'https://cdn.example.com/a.png'
