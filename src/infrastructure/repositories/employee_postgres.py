from typing import Optional
from uuid import UUID

from sqlalchemy import Time, cast, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.auth import EmployeeAuthDTO
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.employee import (
    EmployeeBaseDTO,
    EmployeeOutDTO,
    UpdateEmployeeDTO,
)
from src.domain.repositories.employee import EmployeeRepository
from src.infrastructure.database.models.employees import Employee
from src.infrastructure.database.models.schedule_block import ScheduleBlock


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

    async def get_employee(
        self, id: UUID, company_id: UUID
    ) -> Optional[EmployeeOutDTO]:
        try:
            query = select(Employee).where(
                Employee.id.__eq__(id),
                Employee.company_id.__eq__(company_id),
                Employee.is_deleted.__eq__(False),
            )
            result = await self.session.execute(query)
            employee = result.scalar_one_or_none()

            if employee is None:
                return None

            return EmployeeOutDTO.model_validate(employee)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_employee_auth_by_phone(self, phone: str) -> Optional[EmployeeAuthDTO]:
        try:
            query = select(Employee).where(
                Employee.phone.__eq__(phone), Employee.is_deleted.__eq__(False)
            )
            result = await self.session.execute(query)
            employee = result.scalar_one_or_none()
            if employee is None:
                return None
            return EmployeeAuthDTO.model_validate(employee)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def list_employees(
        self, pagination: PaginationParamsDTO, company_id: UUID
    ) -> list[EmployeeOutDTO]:
        try:
            now_time = cast(func.current_timestamp(), Time)
            has_active_block = (
                select(ScheduleBlock.id)
                .where(
                    ScheduleBlock.employee_id.__eq__(Employee.id),
                    ScheduleBlock.company_id.__eq__(company_id),
                    ScheduleBlock.is_deleted.__eq__(False),
                    ScheduleBlock.is_block.__eq__(True),
                    ScheduleBlock.start_date.__le__(func.current_date()),
                    ScheduleBlock.end_date.__ge__(func.current_date()),
                    ScheduleBlock.start_time.__le__(now_time),
                    ScheduleBlock.end_time.__ge__(now_time),
                )
                .exists()
            )

            query = (
                select(
                    Employee,
                    has_active_block.label('is_block'),
                )
                .where(
                    Employee.is_deleted.__eq__(False),
                    Employee.company_id.__eq__(company_id),
                )
                .order_by(Employee.created_at.desc())
            )

            if pagination.filter_by and pagination.filter_value:
                column = getattr(Employee, pagination.filter_by)
                query = query.where(column.ilike(f'%{pagination.filter_value}%'))

            query = query.offset(pagination.offset).limit(pagination.limit)
            result = await self.session.execute(query)
            rows = result.all()

            employees: list[EmployeeOutDTO] = []
            for employee, is_block in rows:
                employee_dto = EmployeeOutDTO.model_validate(employee)
                employee_dto.is_block = bool(is_block)
                employees.append(employee_dto)

            return employees
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def update_employee(
        self, id: UUID, employee: UpdateEmployeeDTO, company_id: UUID
    ) -> Optional[EmployeeOutDTO]:
        try:
            update_data = employee.model_dump(exclude_unset=True, exclude_none=True)

            stmt = (
                update(Employee)
                .where(
                    Employee.id.__eq__(id),
                    Employee.is_deleted.__eq__(False),
                    Employee.company_id.__eq__(company_id),
                )
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

    async def delete_employee(self, id: UUID, company_id: UUID) -> bool:
        try:
            query = (
                update(Employee)
                .where(
                    Employee.id.__eq__(id),
                    Employee.is_deleted.__eq__(False),
                    Employee.company_id.__eq__(company_id),
                )
                .values(is_deleted=True)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            return result.rowcount > 0
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
