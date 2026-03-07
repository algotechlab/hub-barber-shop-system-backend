from typing import Annotated

from fastapi import Depends

from src.domain.service.schedule_block import ScheduleBlockService
from src.domain.use_case.schedule_block import ScheduleBlockUseCase
from src.infrastructure.repositories.schedule_block_postgres import (
    ScheduleBlockRepositoryPostgres,
)
from src.interface.api.v1.controller.schedule_block import ScheduleBlockController
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep


async def get_schedule_block_controller(
    session: VerifiedSessionDep,
) -> ScheduleBlockController:
    schedule_block_repository = ScheduleBlockRepositoryPostgres(session)
    schedule_block_service = ScheduleBlockService(schedule_block_repository)
    schedule_block_use_case = ScheduleBlockUseCase(schedule_block_service)
    return ScheduleBlockController(schedule_block_use_case)


ScheduleBlockControllerDep = Annotated[
    ScheduleBlockController, Depends(get_schedule_block_controller)
]
