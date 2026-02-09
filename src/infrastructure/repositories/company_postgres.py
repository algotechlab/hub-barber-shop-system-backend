from typing import List
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.company import CompanyDTO, CreateCompanyDTO
from src.domain.repositories.company import CompanyRepository
from src.infrastructure.database.models.companies import Company


class CompanyRepositoryPostgres(CompanyRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_if_company_exists(self, slug: str) -> bool:
        try:
            query = select(Company).where(Company.slug.__eq__(slug))
            result = await self.session.execute(query)
            company = result.scalar_one_or_none()
            return company is not None
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def create_company(self, company: CreateCompanyDTO) -> CompanyDTO:
        try:
            company = Company(**company.model_dump())
            self.session.add(company)
            await self.session.commit()
            await self.session.refresh(company)
            return CompanyDTO.model_validate(company)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_company(self, id: UUID) -> CompanyDTO:
        try:
            query = select(Company).where(Company.id.__eq__(id))
            result = await self.session.execute(query)
            company = result.scalar_one_or_none()
            if company is None:
                return None
            return CompanyDTO.model_validate(company)
        except Exception:
            await self.session.rollback()

    async def list_companies(self) -> List[CompanyDTO]:
        try:
            query = select(Company).where(Company.is_deleted.__eq__(False))
            result = await self.session.execute(query)
            companies = result.scalars().all()
            return [CompanyDTO.model_validate(company) for company in companies]
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def delete_company(self, id: UUID) -> bool:
        try:
            stmt = (
                update(Company)
                .where(Company.id.__eq__(id), Company.is_deleted.__eq__(False))
                .values(is_deleted=True)
                .returning(Company)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()

            updated_company = result.scalar_one_or_none()
            return updated_company is not None
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
