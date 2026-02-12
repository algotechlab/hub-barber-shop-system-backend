from typing import List, Optional
from uuid import UUID

from src.domain.dtos.service import CreateServiceDTO, ServiceDTO, UpdateServiceDTO
from src.domain.execptions.service import ServiceNotFoundException
from src.domain.service.service import ServiceService


class ServiceUseCase:
    def __init__(self, service_service: ServiceService):
        self.service_service = service_service

    async def create_service(self, service: CreateServiceDTO) -> ServiceDTO:
        return await self.service_service.create_service(service)

    async def get_service(self, id: UUID, company_id: UUID) -> Optional[ServiceDTO]:
        service = await self.service_service.get_service(id, company_id)
        if service is None:
            raise ServiceNotFoundException('Serviço não encontrado')
        return service

    async def list_services(self, company_id: UUID) -> List[ServiceDTO]:
        return await self.service_service.list_services(company_id)

    async def update_service(
        self, id: UUID, service: UpdateServiceDTO, company_id: UUID
    ) -> Optional[ServiceDTO]:
        updated_service = await self.service_service.update_service(
            id, service, company_id
        )
        if updated_service is None:
            raise ServiceNotFoundException('Serviço não encontrado')
        return updated_service

    async def delete_service(self, id: UUID, company_id: UUID) -> bool:
        deleted = await self.service_service.delete_service(id, company_id)
        if not deleted:
            raise ServiceNotFoundException('Serviço não encontrado')
        return deleted
