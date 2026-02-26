from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.company import CreateCompanyDTO
from src.domain.service.company import CompanyService

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_check_if_company_exists_delegates_to_repository():
    repo = AsyncMock()
    repo.check_if_company_exists.return_value = True
    service = CompanyService(repo)

    result = await service.check_if_company_exists('slug')

    repo.check_if_company_exists.assert_awaited_once_with('slug')
    assert result is True


@pytest.mark.asyncio
async def test_create_company_delegates_to_repository():
    repo = AsyncMock()
    service = CompanyService(repo)
    dto = CreateCompanyDTO(
        name='N',
        slug='s',
        is_active=True,
        owner_id=uuid4(),
    )
    repo.create_company.return_value = AsyncMock()

    await service.create_company(dto)

    repo.create_company.assert_awaited_once_with(dto)


@pytest.mark.asyncio
async def test_get_company_delegates_to_repository():
    repo = AsyncMock()
    service = CompanyService(repo)
    company_id = uuid4()
    repo.get_company.return_value = None

    result = await service.get_company(company_id)

    repo.get_company.assert_awaited_once_with(company_id)
    assert result is None


@pytest.mark.asyncio
async def test_list_companies_delegates_to_repository():
    repo = AsyncMock()
    service = CompanyService(repo)
    repo.list_companies.return_value = []

    pagination = PaginationParamsDTO()
    result = await service.list_companies(pagination)

    repo.list_companies.assert_awaited_once_with(pagination)
    assert result == []


@pytest.mark.asyncio
async def test_delete_company_delegates_to_repository():
    repo = AsyncMock()
    service = CompanyService(repo)
    company_id = uuid4()
    repo.delete_company.return_value = True

    result = await service.delete_company(company_id)

    repo.delete_company.assert_awaited_once_with(company_id)
    assert result is True


@pytest.mark.asyncio
async def test_list_companies_slug_delegates_to_repository():
    repo = AsyncMock()
    service = CompanyService(repo)
    repo.list_companies_slug.return_value = []

    result = await service.list_companies_slug('slug-x')

    repo.list_companies_slug.assert_awaited_once_with('slug-x')
    assert result == []
