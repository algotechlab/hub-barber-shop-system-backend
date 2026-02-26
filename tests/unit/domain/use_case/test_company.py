from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.company import CompanyDTO, CreateCompanyDTO
from src.domain.exceptions.company import (
    CompanyAlreadyExistsException,
    CompanyNotFoundException,
)
from src.domain.use_case.company import CompanyUseCase

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_company_raises_when_slug_exists():
    service = AsyncMock()
    service.check_if_company_exists.return_value = True
    use_case = CompanyUseCase(service)

    with pytest.raises(CompanyAlreadyExistsException):
        await use_case.create_company(
            CreateCompanyDTO(
                name='N',
                slug='dup',
                is_active=True,
                owner_id=uuid4(),
            )
        )


@pytest.mark.asyncio
async def test_create_company_returns_created_company():
    service = AsyncMock()
    service.check_if_company_exists.return_value = False
    created = CompanyDTO(
        id=uuid4(),
        name='N',
        slug='s',
        is_active=True,
        owner_id=uuid4(),
    )
    service.create_company.return_value = created
    use_case = CompanyUseCase(service)

    result = await use_case.create_company(
        CreateCompanyDTO(
            name='N',
            slug='s',
            is_active=True,
            owner_id=created.owner_id,
        )
    )

    assert result == created


@pytest.mark.asyncio
async def test_get_company_raises_when_not_found():
    service = AsyncMock()
    service.get_company.return_value = None
    use_case = CompanyUseCase(service)

    with pytest.raises(CompanyNotFoundException):
        await use_case.get_company(uuid4())


@pytest.mark.asyncio
async def test_get_company_returns_company_when_found():
    service = AsyncMock()
    company = CompanyDTO(
        id=uuid4(),
        name='N',
        slug='s',
        is_active=True,
        owner_id=uuid4(),
    )
    service.get_company.return_value = company
    use_case = CompanyUseCase(service)

    result = await use_case.get_company(company.id)

    assert result == company


@pytest.mark.asyncio
async def test_list_companies_delegates_to_service():
    service = AsyncMock()
    service.list_companies.return_value = []
    use_case = CompanyUseCase(service)

    pagination = PaginationParamsDTO()
    result = await use_case.list_companies(pagination)

    assert result == []
    service.list_companies.assert_awaited_once_with(pagination)


@pytest.mark.asyncio
async def test_delete_company_raises_when_not_deleted():
    service = AsyncMock()
    service.delete_company.return_value = False
    use_case = CompanyUseCase(service)

    with pytest.raises(CompanyNotFoundException):
        await use_case.delete_company(uuid4())


@pytest.mark.asyncio
async def test_delete_company_returns_true_when_deleted():
    service = AsyncMock()
    service.delete_company.return_value = True
    use_case = CompanyUseCase(service)

    result = await use_case.delete_company(uuid4())

    assert result is True


@pytest.mark.asyncio
async def test_list_companies_slug_returns_companies_when_found():
    service = AsyncMock()
    companies = [
        CompanyDTO(
            id=uuid4(),
            name='N',
            slug='slug-x',
            is_active=True,
            owner_id=uuid4(),
        )
    ]
    service.list_companies_slug.return_value = companies
    use_case = CompanyUseCase(service)

    result = await use_case.list_companies_slug('slug-x')

    assert result == companies
    service.list_companies_slug.assert_awaited_once_with('slug-x')


@pytest.mark.asyncio
async def test_list_companies_slug_raises_when_not_found():
    service = AsyncMock()
    service.list_companies_slug.return_value = []
    use_case = CompanyUseCase(service)

    with pytest.raises(CompanyNotFoundException):
        await use_case.list_companies_slug('slug-inexistente')
