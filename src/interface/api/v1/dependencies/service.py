from typing import Annotated

from fastapi import Depends

from src.domain.service.service import ServiceService
from src.domain.use_case.service import ServiceUseCase
from src.infrastructure.repositories.service_postgres import ServiceRepositoryPostgres
from src.infrastructure.storage.s3 import S3Storage
from src.interface.api.v1.controller.service import ServiceController
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep


async def get_service_controller(session: VerifiedSessionDep) -> ServiceController:
    """
    Singleton para o controller de serviços.
    """
    service_repository = ServiceRepositoryPostgres(session)
    service_service = ServiceService(service_repository)
    service_use_case = ServiceUseCase(service_service)
    storage = S3Storage.from_settings()
    return ServiceController(service_use_case, storage)


ServiceRepositoryDep = Annotated[ServiceController, Depends(get_service_controller)]
