from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.employee import (
    EmployeeBaseDTO,
    EmployeeOutDTO,
    UpdateEmployeeDTO,
)
from src.domain.repositories.employee import EmployeeRepository
from src.infrastructure.database.models.employees import Employee


class EmployeeRepositoryPostgres(EmployeeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_employee(self, employee: EmployeeBaseDTO) -> EmployeeOutDTO:
        try:
            employee = Employee(**employee.model_dump())
            self.session.add(employee)
            await self.session.commit()
            await self.session.refresh(employee)
            return EmployeeOutDTO.model_validate(employee)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_employee(self, id: UUID) -> Optional[EmployeeOutDTO]:
        try:
            query = select(Employee).where(
                Employee.id.__eq__(id), Employee.is_deleted.__eq__(False)
            )
            result = await self.session.execute(query)
            employee = result.scalar_one_or_none()

            if employee is None:
                return None

            return EmployeeOutDTO.model_validate(employee)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def list_employees(
        self, pagination: PaginationParamsDTO
    ) -> list[EmployeeOutDTO]:
        try:
            query = select(Employee).where(Employee.is_deleted.__eq__(False))

            if pagination.filter_by and pagination.filter_value:
                query = query.filter(
                    getattr(Employee, pagination.filter_by).__eq__(
                        pagination.filter_value
                    )
                )

            result = await self.session.execute(query)
            employees = result.scalars().all()
            return [EmployeeOutDTO.model_validate(employee) for employee in employees]
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def update_employee(
        self, id: UUID, employee: UpdateEmployeeDTO
    ) -> Optional[EmployeeOutDTO]:
        try:
            update_data = employee.model_dump(exclude_unset=True, exclude_none=True)

            stmt = (
                update(Employee)
                .where(Employee.id.__eq__(id), Employee.is_deleted.__eq__(False))
                .values(**update_data)
                .returning(Employee)
            )

            result = await self.session.execute(stmt)
            await self.session.commit()

            updated_employee = result.scalar_one_or_none()

            if updated_employee is None:
                return None

            return EmployeeOutDTO.model_validate(updated_employee)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def delete_employee(self, id: UUID) -> bool:
        try:
            query = (
                update(Employee)
                .where(Employee.id.__eq__(id), Employee.is_deleted.__eq__(False))
                .values(is_deleted=True)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            return result.rowcount > 0
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
