from typing import Annotated

from fastapi import Depends

from src.domain.service.schedule import ScheduleService
from src.domain.use_case.schedule import ScheduleUseCase
from src.infrastructure.repositories.schedule_postgres import ScheduleRepositoryPostgres
from src.interface.api.v1.controller.schedule import ScheduleController
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep


async def get_schedule_controller(
    session: VerifiedSessionDep,
) -> ScheduleController:
    schedule_repository = ScheduleRepositoryPostgres(session)
    schedule_service = ScheduleService(schedule_repository)
    schedule_use_case = ScheduleUseCase(schedule_service)
    return ScheduleController(schedule_use_case)


ScheduleRepositoryDep = Annotated[ScheduleController, Depends(get_schedule_controller)]
