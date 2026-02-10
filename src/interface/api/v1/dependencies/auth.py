from typing import Annotated

from fastapi import Depends

from src.domain.service.employee import EmployeeService
from src.domain.service.owner import OwnerService
from src.domain.service.users import UsersService
from src.domain.use_case.auth import AuthUseCase
from src.infrastructure.repositories.employee_postgres import EmployeeRepositoryPostgres
from src.infrastructure.repositories.owner_postgres import OwnerRepositoryPostgres
from src.infrastructure.repositories.users_postgres import UsersRepositoryPostgres
from src.interface.api.v1.controller.auth import AuthController
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep


async def get_auth_controller(session: VerifiedSessionDep) -> AuthController:
    owner_repository = OwnerRepositoryPostgres(session)
    owner_service = OwnerService(owner_repository)

    employee_repository = EmployeeRepositoryPostgres(session)
    employee_service = EmployeeService(employee_repository)

    users_repository = UsersRepositoryPostgres(session)
    users_service = UsersService(users_repository)

    auth_use_case = AuthUseCase(owner_service, employee_service, users_service)
    return AuthController(auth_use_case)


AuthControllerDep = Annotated[AuthController, Depends(get_auth_controller)]
