from abc import abstractmethod
from typing import List
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.company import CompanyDTO, CreateCompanyDTO


class CompanyRepository:
    @abstractmethod
    async def check_if_company_exists(self, slug: str) -> bool: ...

    @abstractmethod
    async def create_company(self, company: CreateCompanyDTO) -> CompanyDTO: ...

    @abstractmethod
    async def get_company(self, id: UUID) -> CompanyDTO: ...

    @abstractmethod
    async def list_companies(
        self, pagination: PaginationParamsDTO
    ) -> List[CompanyDTO]: ...

    @abstractmethod
    async def delete_company(self, id: UUID) -> bool: ...

    @abstractmethod
    async def list_companies_slug(self, slug: str) -> List[CompanyDTO]: ...
