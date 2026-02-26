from typing import List
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.company import CompanyDTO, CreateCompanyDTO
from src.domain.exceptions.company import (
    CompanyAlreadyExistsException,
    CompanyNotFoundException,
)
from src.domain.service.company import CompanyService


class CompanyUseCase:
    def __init__(self, company_service: CompanyService):
        self.company_service = company_service

    async def create_company(self, company: CreateCompanyDTO) -> CompanyDTO:
        if await self.company_service.check_if_company_exists(company.slug):
            raise CompanyAlreadyExistsException(
                f'Compania com slug {company.slug} já existe'
            )
        created_company = await self.company_service.create_company(company)
        return created_company

    async def get_company(self, id: UUID) -> CompanyDTO:
        company = await self.company_service.get_company(id)
        if company is None:
            raise CompanyNotFoundException(f'Compania com id {id} não encontrada')
        return company

    async def list_companies(self, pagination: PaginationParamsDTO) -> List[CompanyDTO]:
        return await self.company_service.list_companies(pagination)

    async def delete_company(self, id: UUID) -> bool:
        deleted = await self.company_service.delete_company(id)
        if not deleted:
            raise CompanyNotFoundException(f'Compania com id {id} não encontrada')
        return deleted

    async def list_companies_slug(self, slug: str) -> List[CompanyDTO]:
        companies = await self.company_service.list_companies_slug(slug)
        if not companies:
            raise CompanyNotFoundException(f'Companias com slug {slug} não encontradas')
        return companies
