from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status

from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee_or_user,
)
from src.interface.api.v1.dependencies.common.pagination import PaginationParamsDep
from src.interface.api.v1.dependencies.schedule import ScheduleRepositoryDep
from src.interface.api.v1.schema.schedule import (
    CreateScheduleSchema,
    ScheduleOutSchema,
    UpdateScheduleSchema,
)

tags_metadata = {
    'name': 'Agendamentos',
    'description': ('Modulo de agendamentos.'),
}

router = APIRouter(
    prefix='/schedule',
    tags=[tags_metadata['name']],
    dependencies=[Depends(require_current_employee_or_user)],
)


@router.get(
    '',
    description='Rota para listar agendamentos',
    status_code=status.HTTP_200_OK,
    response_model=List[ScheduleOutSchema],
)
async def list_schedules(
    controller: ScheduleRepositoryDep, pagination: PaginationParamsDep, request: Request
) -> List[ScheduleOutSchema]:
    return await controller.list_schedules(
        pagination, company_id=request.state.company_id
    )


@router.post(
    '',
    description='Rota para criar agendamento',
    status_code=status.HTTP_201_CREATED,
    response_model=ScheduleOutSchema,
)
async def create_schedule(
    controller: ScheduleRepositoryDep, schedule: CreateScheduleSchema, request: Request
) -> ScheduleOutSchema:
    return await controller.create_schedule(
        schedule, company_id=request.state.company_id
    )


@router.get(
    '/{schedule_id}',
    description='Rota para buscar agendamento',
    status_code=status.HTTP_200_OK,
    response_model=ScheduleOutSchema,
)
async def get_schedule(
    controller: ScheduleRepositoryDep, schedule_id: UUID, request: Request
) -> ScheduleOutSchema:
    return await controller.get_schedule(
        schedule_id, company_id=request.state.company_id
    )


@router.patch(
    '/{schedule_id}',
    description='Rota para atualizar agendamento',
    status_code=status.HTTP_200_OK,
    response_model=ScheduleOutSchema,
)
async def update_schedule(
    controller: ScheduleRepositoryDep,
    schedule_id: UUID,
    schedule: UpdateScheduleSchema,
    request: Request,
) -> ScheduleOutSchema:
    return await controller.update_schedule(
        schedule_id, schedule, company_id=request.state.company_id
    )


@router.delete(
    '/{schedule_id}',
    description='Rota para deletar agendamento',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_schedule(
    controller: ScheduleRepositoryDep, schedule_id: UUID, request: Request
) -> Response:
    await controller.delete_schedule(schedule_id, company_id=request.state.company_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
