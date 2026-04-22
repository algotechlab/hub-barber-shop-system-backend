from typing import Annotated

from fastapi import Depends

from src.domain.service.cash_register import CashRegisterService
from src.domain.use_case.cash_register import CashRegisterUseCase
from src.infrastructure.repositories.cash_register_postgres import (
    CashRegisterRepositoryPostgres,
)
from src.interface.api.v1.controller.cash_register import CashRegisterController
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep


async def get_cash_register_controller(
    session: VerifiedSessionDep,
) -> CashRegisterController:
    repository = CashRegisterRepositoryPostgres(session)
    service = CashRegisterService(repository)
    use_case = CashRegisterUseCase(service)
    return CashRegisterController(use_case)


CashRegisterControllerDep = Annotated[
    CashRegisterController, Depends(get_cash_register_controller)
]
