from typing import List, Optional
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.service import CreateServiceDTO, ServiceDTO, UpdateServiceDTO
from src.domain.repositories.service import ServiceRepository


class ServiceService:
    def __init__(self, service_repository: ServiceRepository):
        self.service_repository = service_repository

    async def create_service(self, service: CreateServiceDTO) -> ServiceDTO:
        return await self.service_repository.create_service(service)

    async def get_service(self, id: UUID, company_id: UUID) -> Optional[ServiceDTO]:
        return await self.service_repository.get_service(id, company_id)

    async def list_services(
        self, pagination: PaginationParamsDTO, company_id: UUID
    ) -> List[ServiceDTO]:
        return await self.service_repository.list_services(pagination, company_id)

    async def update_service(
        self, id: UUID, service: UpdateServiceDTO, company_id: UUID
    ) -> Optional[ServiceDTO]:
        return await self.service_repository.update_service(id, service, company_id)

    async def delete_service(self, id: UUID, company_id: UUID) -> bool:
        return await self.service_repository.delete_service(id, company_id)
