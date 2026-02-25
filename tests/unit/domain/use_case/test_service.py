from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.service import CreateServiceDTO, ServiceDTO, UpdateServiceDTO
from src.domain.exceptions.service import ServiceNotFoundException
from src.domain.use_case.service import ServiceUseCase

pytestmark = pytest.mark.unit


def _service(company_id):
    return ServiceDTO(
        id=uuid4(),
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


@pytest.mark.asyncio
async def test_create_service_delegates_to_service_layer():
    service = AsyncMock()
    use_case = ServiceUseCase(service)
    company_id = uuid4()
    dto = CreateServiceDTO(
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
    expected = _service(company_id)
    service.create_service.return_value = expected

    result = await use_case.create_service(dto)

    service.create_service.assert_awaited_once_with(dto)
    assert result == expected


@pytest.mark.asyncio
async def test_get_service_raises_when_not_found():
    service = AsyncMock()
    service.get_service.return_value = None
    use_case = ServiceUseCase(service)

    with pytest.raises(ServiceNotFoundException):
        await use_case.get_service(uuid4(), uuid4())


@pytest.mark.asyncio
async def test_get_service_returns_when_found():
    service = AsyncMock()
    company_id = uuid4()
    expected = _service(company_id)
    service.get_service.return_value = expected
    use_case = ServiceUseCase(service)

    result = await use_case.get_service(expected.id, company_id)

    assert result == expected


@pytest.mark.asyncio
async def test_list_services_delegates_to_service_layer():
    service = AsyncMock()
    service.list_services.return_value = []
    use_case = ServiceUseCase(service)
    company_id = uuid4()

    pagination = PaginationParamsDTO()
    result = await use_case.list_services(pagination, company_id)

    service.list_services.assert_awaited_once_with(pagination, company_id)
    assert result == []


@pytest.mark.asyncio
async def test_update_service_raises_when_not_found():
    service = AsyncMock()
    service.update_service.return_value = None
    use_case = ServiceUseCase(service)

    with pytest.raises(ServiceNotFoundException):
        await use_case.update_service(uuid4(), UpdateServiceDTO(name='X'), uuid4())


@pytest.mark.asyncio
async def test_update_service_returns_when_found():
    service = AsyncMock()
    company_id = uuid4()
    expected = _service(company_id)
    service.update_service.return_value = expected
    use_case = ServiceUseCase(service)

    result = await use_case.update_service(
        expected.id, UpdateServiceDTO(name='X'), company_id
    )

    assert result == expected


@pytest.mark.asyncio
async def test_delete_service_raises_when_not_deleted():
    service = AsyncMock()
    service.delete_service.return_value = False
    use_case = ServiceUseCase(service)

    with pytest.raises(ServiceNotFoundException):
        await use_case.delete_service(uuid4(), uuid4())


@pytest.mark.asyncio
async def test_delete_service_returns_true_when_deleted():
    service = AsyncMock()
    service.delete_service.return_value = True
    use_case = ServiceUseCase(service)

    result = await use_case.delete_service(uuid4(), uuid4())

    assert result is True
