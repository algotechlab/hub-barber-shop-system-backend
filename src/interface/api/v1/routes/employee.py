from uuid import UUID

from fastapi import APIRouter, status

from src.interface.api.v1.dependencies.common.pagination import PaginationParamsDep
from src.interface.api.v1.dependencies.employee import EmployeeRepositoryDep
from src.interface.api.v1.schema.employee import (
    CreateEmployeeSchema,
    EmployeeOutSchema,
    EmployeeSchema,
    UpdateEmployeeSchema,
)

router = APIRouter(
    prefix='/employees',
    tags=['employees'],
)


@router.get(
    '', description='Rota para listar funcionários', status_code=status.HTTP_200_OK
)
async def list_employees(
    controller: EmployeeRepositoryDep, pagination: PaginationParamsDep
) -> list[EmployeeSchema]:
    return await controller.list_employees(pagination)


@router.post(
    '',
    description='Rota para criar funcionário',
    status_code=status.HTTP_201_CREATED,
    response_model=EmployeeOutSchema,
)
async def create_employee(
    controller: EmployeeRepositoryDep, employee: CreateEmployeeSchema
) -> EmployeeOutSchema:
    return await controller.create_employee(employee)


@router.get(
    '/{employee_id}',
    description='Rota para buscar funcionário',
    status_code=status.HTTP_200_OK,
    response_model=EmployeeOutSchema,
)
async def get_employee(
    controller: EmployeeRepositoryDep, employee_id: UUID
) -> EmployeeOutSchema:
    return await controller.get_employee(employee_id)


@router.patch(
    '/{employee_id}',
    description='Rota para atualizar funcionário',
    status_code=status.HTTP_200_OK,
    response_model=EmployeeOutSchema,
)
async def update_employee(
    controller: EmployeeRepositoryDep, employee_id: UUID, employee: UpdateEmployeeSchema
) -> EmployeeOutSchema:
    return await controller.update_employee(employee_id, employee)


@router.delete(
    '/{employee_id}',
    description='Rota para deletar funcionário',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_employee(controller: EmployeeRepositoryDep, employee_id: UUID) -> None:
    return await controller.delete_employee(employee_id)
