from typing import Annotated

from fastapi import Depends

from src.domain.service.company import CompanyService
from src.domain.use_case.company import CompanyUseCase
from src.infrastructure.repositories.company_postgres import CompanyRepositoryPostgres
from src.interface.api.v1.controller.company import CompanyController
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep


async def get_company_controller(
    session: VerifiedSessionDep,
) -> CompanyController:
    """
    Singleton para o controller de companias.
    """
    company_repository = CompanyRepositoryPostgres(session)
    company_service = CompanyService(company_repository)
    company_use_case = CompanyUseCase(company_service)
    return CompanyController(company_use_case)


CompanyRepositoryDep = Annotated[CompanyController, Depends(get_company_controller)]
