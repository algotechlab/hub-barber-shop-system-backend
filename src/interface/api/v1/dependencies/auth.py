from typing import Annotated

from fastapi import Depends

from src.domain.service.owner import OwnerService
from src.domain.use_case.auth import AuthUseCase
from src.infrastructure.repositories.owner_postgres import OwnerRepositoryPostgres
from src.interface.api.v1.controller.auth import AuthController
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep


async def get_auth_controller(session: VerifiedSessionDep) -> AuthController:
    owner_repository = OwnerRepositoryPostgres(session)
    owner_service = OwnerService(owner_repository)
    auth_use_case = AuthUseCase(owner_service)
    return AuthController(auth_use_case)


AuthControllerDep = Annotated[AuthController, Depends(get_auth_controller)]
