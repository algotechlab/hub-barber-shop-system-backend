from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.service import CreateServiceDTO, ServiceDTO, UpdateServiceDTO
from src.domain.service.service import ServiceService

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_service_delegates_to_repository():
    repo = AsyncMock()
    service = ServiceService(repo)
    dto = CreateServiceDTO(
        name='Corte',
        description='Desc',
        price=Decimal('10'),
        duration=30,
        category='Cat',
        time_to_spend=30,
        status=True,
        url_image='https://cdn.example.com/a.png',
        company_id=uuid4(),
    )
    out = ServiceDTO(
        id=uuid4(),
        name=dto.name,
        description=dto.description,
        price=dto.price,
        duration=dto.duration,
        category=dto.category,
        time_to_spend=dto.time_to_spend,
        status=dto.status,
        url_image=dto.url_image,
        company_id=dto.company_id,
    )
    repo.create_service.return_value = out

    result = await service.create_service(dto)

    repo.create_service.assert_awaited_once_with(dto)
    assert result == out


@pytest.mark.asyncio
async def test_get_service_delegates_to_repository():
    repo = AsyncMock()
    service = ServiceService(repo)
    repo.get_service.return_value = None

    result = await service.get_service(uuid4(), uuid4())

    repo.get_service.assert_awaited_once()
    assert result is None


@pytest.mark.asyncio
async def test_list_services_delegates_to_repository():
    repo = AsyncMock()
    service = ServiceService(repo)
    company_id = uuid4()
    repo.list_services.return_value = []

    result = await service.list_services(company_id)

    repo.list_services.assert_awaited_once_with(company_id)
    assert result == []


@pytest.mark.asyncio
async def test_update_service_delegates_to_repository():
    repo = AsyncMock()
    service = ServiceService(repo)
    repo.update_service.return_value = None

    result = await service.update_service(uuid4(), UpdateServiceDTO(name='X'), uuid4())

    repo.update_service.assert_awaited_once()
    assert result is None


@pytest.mark.asyncio
async def test_delete_service_delegates_to_repository():
    repo = AsyncMock()
    service = ServiceService(repo)
    repo.delete_service.return_value = True

    result = await service.delete_service(uuid4(), uuid4())

    repo.delete_service.assert_awaited_once()
    assert result is True
