from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status

from src.domain.exceptions.auth import UnauthorizedException
from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee,
    require_current_employee_or_user,
)
from src.interface.api.v1.dependencies.common.pagination import PaginationParamsDep
from src.interface.api.v1.dependencies.schedule import ScheduleRepositoryDep
from src.interface.api.v1.schema.schedule import (
    CloseScheduleSchema,
    CreateScheduleSchema,
    ScheduleFinanceOutSchema,
    ScheduleOutSchema,
    SlotOutSchema,
    SlotsInSchema,
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
    controller: ScheduleRepositoryDep,
    pagination: PaginationParamsDep,
    request: Request,
    employee_id: UUID | None = None,
) -> List[ScheduleOutSchema]:
    user_id = getattr(request.state, 'user_id', None)
    return await controller.list_schedules(
        pagination,
        company_id=request.state.company_id,
        employee_id=employee_id,
        user_id=user_id,
    )


@router.get(
    '/me',
    description='Rota para listar a agenda do usuário autenticado',
    status_code=status.HTTP_200_OK,
    response_model=List[ScheduleOutSchema],
)
async def list_user_schedules(
    controller: ScheduleRepositoryDep,
    pagination: PaginationParamsDep,
    request: Request,
) -> List[ScheduleOutSchema]:
    user_id = getattr(request.state, 'user_id', None)
    if user_id is None:
        raise UnauthorizedException('Apenas usuário pode consultar a própria agenda')

    return await controller.get_schedule_by_user_id(
        pagination, company_id=request.state.company_id, user_id=user_id
    )


@router.get(
    '/history',
    description='Lista histórico: cancelados e/ou finalizados (fechamento financeiro).',
    status_code=status.HTTP_200_OK,
    response_model=List[ScheduleOutSchema],
)
async def list_schedule_history(
    controller: ScheduleRepositoryDep,
    pagination: PaginationParamsDep,
    request: Request,
    include_canceled: bool = True,
    include_finished: bool = True,
    employee_id: UUID | None = None,
) -> List[ScheduleOutSchema]:
    user_id = getattr(request.state, 'user_id', None)
    return await controller.list_schedule_history(
        pagination,
        company_id=request.state.company_id,
        include_canceled=include_canceled,
        include_finished=include_finished,
        employee_id=employee_id,
        user_id=user_id,
    )


@router.get(
    '/slots',
    description='Rota para listar slots de agendamento',
    status_code=status.HTTP_200_OK,
    response_model=List[SlotOutSchema],
)
async def get_slots(
    controller: ScheduleRepositoryDep,
    request: Request,
    slots: SlotsInSchema = Depends(),
) -> List[SlotOutSchema]:
    return await controller.get_slots(slots, company_id=request.state.company_id)


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


@router.patch(
    '/{employee_id}/block',
    description='Rota para bloquear horário de um funcionário',
    status_code=status.HTTP_200_OK,
)
async def block_schedule(
    controller: ScheduleRepositoryDep,
    employee_id: UUID,
    request: Request,
) -> Response:
    await controller.block_schedule(employee_id, company_id=request.state.company_id)
    return Response(status_code=status.HTTP_200_OK)


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


@router.post(
    '/{schedule_id}/close',
    description='Rota para fechamento do agendamento e persistência financeira',
    status_code=status.HTTP_201_CREATED,
    response_model=ScheduleFinanceOutSchema,
    dependencies=[Depends(require_current_employee)],
)
async def close_schedule(
    controller: ScheduleRepositoryDep,
    schedule_id: UUID,
    schedule_close: CloseScheduleSchema,
    request: Request,
) -> ScheduleFinanceOutSchema:
    return await controller.close_schedule(
        schedule_id=schedule_id,
        schedule_close=schedule_close,
        company_id=request.state.company_id,
        created_by=request.state.employee_id,
    )
