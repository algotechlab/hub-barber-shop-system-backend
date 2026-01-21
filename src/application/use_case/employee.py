from typing import Optional
from uuid import UUID

from src.application.dtos.common.pagination import PaginationParamsDTO
from src.application.dtos.employee import (
    EmployeeBaseDTO,
    EmployeeOutDTO,
    UpdateEmployeeDTO,
)
from src.core.utils.get_argon import hash_password
from src.domain.service.employee import EmployeeService


class EmployeeUseCase:
    def __init__(self, employee_service: EmployeeService):
        self.employee_service = employee_service

    async def list_employees(
        self, pagination: PaginationParamsDTO
    ) -> list[EmployeeOutDTO]:
        return await self.employee_service.list_employees(pagination)

    async def create_employee(self, employee: EmployeeBaseDTO) -> EmployeeOutDTO:
        employee.password = hash_password(employee.password)
        return await self.employee_service.create_employee(employee)

    async def get_employee(self, id: UUID) -> Optional[EmployeeOutDTO]:
        return await self.employee_service.get_employee(id)

    async def update_employee(
        self, id: UUID, employee: UpdateEmployeeDTO
    ) -> Optional[EmployeeOutDTO]:
        return await self.employee_service.update_employee(id, employee)

    async def delete_employee(self, id: UUID) -> Optional[bool]:
        return await self.employee_service.delete_employee(id)
