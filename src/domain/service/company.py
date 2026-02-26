from typing import List
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.company import CompanyDTO, CreateCompanyDTO
from src.domain.repositories.company import CompanyRepository


class CompanyService:
    def __init__(self, company_repository: CompanyRepository):
        self.company_repository = company_repository

    async def check_if_company_exists(self, slug: str) -> bool:
        return await self.company_repository.check_if_company_exists(slug)

    async def create_company(self, company: CreateCompanyDTO) -> CompanyDTO:
        return await self.company_repository.create_company(company)

    async def get_company(self, id: UUID) -> CompanyDTO:
        return await self.company_repository.get_company(id)

    async def list_companies(self, pagination: PaginationParamsDTO) -> List[CompanyDTO]:
        return await self.company_repository.list_companies(pagination)

    async def delete_company(self, id: UUID) -> bool:
        return await self.company_repository.delete_company(id)

    async def list_companies_slug(self, slug: str) -> List[CompanyDTO]:
        return await self.company_repository.list_companies_slug(slug)
