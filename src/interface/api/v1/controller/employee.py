from typing import Optional
from uuid import UUID

from src.domain.dtos.employee import EmployeeBaseDTO, UpdateEmployeeDTO
from src.domain.use_case.employee import EmployeeUseCase
from src.interface.api.v1.schema.common.pagination import PaginationParamsBaseSchema
from src.interface.api.v1.schema.employee import (
    CreateEmployeeSchema,
    EmployeeOutSchema,
    EmployeeSchema,
    UpdateEmployeeSchema,
)


class EmployeeController:
    def __init__(self, employee_use_case: EmployeeUseCase):
        self.employee_use_case = employee_use_case

    async def list_employees(
        self, pagination: PaginationParamsBaseSchema, company_id: UUID
    ) -> list[EmployeeSchema]:
        return await self.employee_use_case.list_employees(pagination, company_id)

    async def create_employee(
        self,
        employee: CreateEmployeeSchema,
        company_id: UUID,
    ) -> EmployeeOutSchema:
        employee_dto = EmployeeBaseDTO(**employee.model_dump(), company_id=company_id)
        created_employee = await self.employee_use_case.create_employee(employee_dto)
        return EmployeeOutSchema(**created_employee.model_dump())

    async def get_employee(
        self, id: UUID, company_id: UUID
    ) -> Optional[EmployeeOutSchema]:
        employee = await self.employee_use_case.get_employee(id, company_id)
        return EmployeeOutSchema(**employee.model_dump())

    async def update_employee(
        self, id: UUID, employee: UpdateEmployeeSchema, company_id: UUID
    ) -> Optional[EmployeeOutSchema]:
        employee_dto = UpdateEmployeeDTO(**employee.model_dump())
        updated_employee = await self.employee_use_case.update_employee(
            id, employee_dto, company_id
        )
        return EmployeeOutSchema(**updated_employee.model_dump())

    async def delete_employee(self, id: UUID, company_id: UUID) -> bool:
        return await self.employee_use_case.delete_employee(id, company_id)
