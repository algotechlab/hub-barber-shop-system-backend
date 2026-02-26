from typing import List
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.company import CreateCompanyDTO
from src.domain.use_case.company import CompanyUseCase
from src.interface.api.v1.schema.company import (
    CompanyOutSchema,
    CreateCompanySchema,
)


class CompanyController:
    def __init__(self, company_use_case: CompanyUseCase):
        self.company_use_case = company_use_case

    async def create_company(
        self, company: CreateCompanySchema, owner_id: UUID
    ) -> CompanyOutSchema:
        company_dto = CreateCompanyDTO(**company.model_dump(), owner_id=owner_id)
        created_company = await self.company_use_case.create_company(company_dto)
        return CompanyOutSchema(**created_company.model_dump())

    async def get_company(self, id: UUID) -> CompanyOutSchema:
        company = await self.company_use_case.get_company(id)
        if company is None:
            return None
        return CompanyOutSchema(**company.model_dump())

    async def list_companies(
        self, pagination: PaginationParamsDTO
    ) -> List[CompanyOutSchema]:
        companies = await self.company_use_case.list_companies(pagination)
        return [CompanyOutSchema(**company.model_dump()) for company in companies]

    async def delete_company(self, id: UUID) -> bool:
        return await self.company_use_case.delete_company(id)

    async def list_companies_slug(self, slug: str) -> List[CompanyOutSchema]:
        companies = await self.company_use_case.list_companies_slug(slug)
        return [CompanyOutSchema(**company.model_dump()) for company in companies]
