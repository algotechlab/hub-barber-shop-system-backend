from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.dtos.service import CreateServiceDTO, ServiceDTO, UpdateServiceDTO


class ServiceRepository(ABC):
    @abstractmethod
    async def create_service(self, service: CreateServiceDTO) -> ServiceDTO: ...

    @abstractmethod
    async def get_service(self, id: UUID, company_id: UUID) -> Optional[ServiceDTO]: ...

    @abstractmethod
    async def list_services(self, company_id: UUID) -> List[ServiceDTO]: ...

    @abstractmethod
    async def update_service(
        self, id: UUID, service: UpdateServiceDTO, company_id: UUID
    ) -> Optional[ServiceDTO]: ...

    @abstractmethod
    async def delete_service(self, id: UUID, company_id: UUID) -> bool: ...
