from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status

from src.interface.api.v1.dependencies.common.auth import require_current_employee
from src.interface.api.v1.dependencies.schedule_block import ScheduleBlockControllerDep
from src.interface.api.v1.schema.schedule_block import (
    CreateScheduleBlockSchema,
    ScheduleBlockOutSchema,
    UpdateScheduleBlockSchema,
)

tags_metadata = {
    'name': 'Blocos de horário',
    'description': ('Modulo de blocos de horário.'),
}

router = APIRouter(
    prefix='/schedule-blocks',
    tags=[tags_metadata['name']],
    dependencies=[Depends(require_current_employee)],
)


@router.post(
    '',
    description='Rota para criar um bloco de horário',
    status_code=status.HTTP_201_CREATED,
    response_model=ScheduleBlockOutSchema,
)
async def create_schedule_block(
    controller: ScheduleBlockControllerDep,
    schedule_block: CreateScheduleBlockSchema,
    request: Request,
) -> ScheduleBlockOutSchema:
    return await controller.create_schedule_block(
        schedule_block, company_id=request.state.company_id
    )


@router.get(
    '/{id}',
    description='Rota para buscar um bloco de horário',
    status_code=status.HTTP_200_OK,
    response_model=ScheduleBlockOutSchema,
)
async def get_schedule_block(
    controller: ScheduleBlockControllerDep,
    id: UUID,
) -> ScheduleBlockOutSchema:
    return await controller.get_schedule_block(id)


@router.patch(
    '/{id}',
    description='Rota para atualizar um bloco de horário',
    status_code=status.HTTP_200_OK,
    response_model=ScheduleBlockOutSchema,
)
async def update_schedule_block(
    controller: ScheduleBlockControllerDep,
    id: UUID,
    schedule_block: UpdateScheduleBlockSchema,
) -> ScheduleBlockOutSchema:
    return await controller.update_schedule_block(id, schedule_block)


@router.delete(
    '/{id}',
    description='Rota para deletar um bloco de horário',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_schedule_block(
    controller: ScheduleBlockControllerDep,
    id: UUID,
) -> None:
    await controller.delete_schedule_block(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
