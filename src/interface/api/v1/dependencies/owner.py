from typing import Annotated

from fastapi import Depends

from src.domain.service.owner import OwnerService
from src.domain.use_case.owner import OwnerUseCase
from src.infrastructure.repositories.owner_postgres import OwnerRepositoryPostgres
from src.interface.api.v1.controller.owner import OwnerController
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep


async def get_owner_controller(
    session: VerifiedSessionDep,
) -> OwnerController:
    owner_repository = OwnerRepositoryPostgres(session)
    owner_service = OwnerService(owner_repository)
    owner_use_case = OwnerUseCase(owner_service)
    return OwnerController(owner_use_case)


OwnerControllerDep = Annotated[OwnerController, Depends(get_owner_controller)]
