from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.company import CompanyDTO
from src.interface.api.v1.controller.company import CompanyController
from src.interface.api.v1.schema.company import CreateCompanySchema

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_company_maps_owner_id_and_returns_schema():
    use_case = AsyncMock()
    owner_id = uuid4()
    company = CompanyDTO(
        id=uuid4(),
        name='N',
        slug='s',
        is_active=True,
        owner_id=owner_id,
    )
    use_case.create_company.return_value = company
    controller = CompanyController(use_case)

    result = await controller.create_company(
        CreateCompanySchema(name='N', slug='s', is_active=True),
        owner_id=owner_id,
    )

    assert result.id == company.id
    assert result.owner_id == owner_id
    use_case.create_company.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_company_returns_none_when_use_case_returns_none():
    use_case = AsyncMock()
    use_case.get_company.return_value = None
    controller = CompanyController(use_case)

    result = await controller.get_company(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_get_company_returns_schema_when_found():
    use_case = AsyncMock()
    company = CompanyDTO(
        id=uuid4(),
        name='N',
        slug='s',
        is_active=True,
        owner_id=uuid4(),
    )
    use_case.get_company.return_value = company
    controller = CompanyController(use_case)

    result = await controller.get_company(company.id)

    assert result is not None
    assert result.id == company.id


@pytest.mark.asyncio
async def test_list_companies_returns_schema_list():
    use_case = AsyncMock()
    company = CompanyDTO(
        id=uuid4(),
        name='N',
        slug='s',
        is_active=True,
        owner_id=uuid4(),
    )
    use_case.list_companies.return_value = [company]
    controller = CompanyController(use_case)

    result = await controller.list_companies()

    assert len(result) == 1
    assert result[0].id == company.id


@pytest.mark.asyncio
async def test_delete_company_delegates_to_use_case():
    use_case = AsyncMock()
    use_case.delete_company.return_value = True
    controller = CompanyController(use_case)
    company_id = uuid4()

    result = await controller.delete_company(company_id)

    use_case.delete_company.assert_awaited_once_with(company_id)
    assert result is True
