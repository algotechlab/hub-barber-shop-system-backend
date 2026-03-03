from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee_or_user,
)
from src.interface.api.v1.dependencies.common.pagination import PaginationParamsDep
from src.interface.api.v1.dependencies.employee import EmployeeRepositoryDep
from src.interface.api.v1.schema.employee import (
    CreateEmployeeSchema,
    EmployeeOutSchema,
    EmployeeSchema,
    UpdateEmployeeSchema,
)

tags_metadata = {
    'name': 'Funcionários',
    'description': ('Modulo de funcionários.'),
}

router = APIRouter(
    prefix='/employees',
    tags=[tags_metadata['name']],
    dependencies=[Depends(require_current_employee_or_user)],
)


@router.get(
    '', description='Rota para listar funcionários', status_code=status.HTTP_200_OK
)
async def list_employees(
    controller: EmployeeRepositoryDep, pagination: PaginationParamsDep, request: Request
) -> list[EmployeeSchema]:
    return await controller.list_employees(
        pagination, company_id=request.state.company_id
    )


@router.post(
    '',
    description='Rota para criar funcionário',
    status_code=status.HTTP_201_CREATED,
    response_model=EmployeeOutSchema,
)
async def create_employee(
    controller: EmployeeRepositoryDep, employee: CreateEmployeeSchema, request: Request
) -> EmployeeOutSchema:
    return await controller.create_employee(
        employee, company_id=request.state.company_id
    )


@router.get(
    '/{employee_id}',
    description='Rota para buscar funcionário',
    status_code=status.HTTP_200_OK,
    response_model=EmployeeOutSchema,
)
async def get_employee(
    controller: EmployeeRepositoryDep, employee_id: UUID, request: Request
) -> EmployeeOutSchema:
    return await controller.get_employee(
        employee_id, company_id=request.state.company_id
    )


@router.patch(
    '/{employee_id}',
    description='Rota para atualizar funcionário',
    status_code=status.HTTP_200_OK,
    response_model=EmployeeOutSchema,
)
async def update_employee(
    controller: EmployeeRepositoryDep,
    employee_id: UUID,
    employee: UpdateEmployeeSchema,
    request: Request,
) -> EmployeeOutSchema:
    return await controller.update_employee(
        employee_id, employee, company_id=request.state.company_id
    )


@router.delete(
    '/{employee_id}',
    description='Rota para deletar funcionário',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_employee(
    controller: EmployeeRepositoryDep, employee_id: UUID, request: Request
) -> None:
    return await controller.delete_employee(
        employee_id, company_id=request.state.company_id
    )
