from typing import Optional
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.employee import (
    EmployeeBaseDTO,
    EmployeeOutDTO,
    UpdateEmployeeDTO,
)
from src.domain.repositories.employee import EmployeeRepository


class EmployeeService:
    def __init__(self, employee_repository: EmployeeRepository):
        self.employee_repository = employee_repository

    async def list_employees(
        self, pagination: PaginationParamsDTO
    ) -> list[EmployeeOutDTO]:
        return await self.employee_repository.list_employees(pagination)

    async def create_employee(self, employee: EmployeeBaseDTO) -> EmployeeOutDTO:
        return await self.employee_repository.create_employee(employee)

    async def get_employee(self, id: UUID) -> Optional[EmployeeOutDTO]:
        return await self.employee_repository.get_employee(id)

    async def update_employee(
        self, id: UUID, employee: UpdateEmployeeDTO
    ) -> Optional[EmployeeOutDTO]:
        return await self.employee_repository.update_employee(id, employee)

    async def delete_employee(self, id: UUID) -> Optional[bool]:
        return await self.employee_repository.delete_employee(id)
