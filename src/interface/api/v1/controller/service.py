from typing import List
from uuid import UUID

from fastapi import UploadFile

from src.domain.dtos.service import CreateServiceDTO, ServiceDTO, UpdateServiceDTO
from src.domain.use_case.service import ServiceUseCase
from src.infrastructure.storage.s3 import S3Storage
from src.interface.api.v1.schema.service import (
    CreateServiceSchema,
    ServiceSchema,
    UpdateServiceSchema,
    UploadServiceImageOutSchema,
)


class ServiceController:
    def __init__(self, service_use_case: ServiceUseCase, storage: S3Storage):
        self.service_use_case = service_use_case
        self.storage = storage

    async def create_service(
        self, service: CreateServiceSchema, company_id: UUID
    ) -> ServiceDTO:
        service_dto = CreateServiceDTO(**service.model_dump(), company_id=company_id)
        created_service = await self.service_use_case.create_service(service_dto)
        return ServiceSchema(**created_service.model_dump())

    async def list_services(self, company_id: UUID) -> List[ServiceSchema]:
        services = await self.service_use_case.list_services(company_id)
        return [ServiceSchema(**service.model_dump()) for service in services]

    async def get_service(self, id: UUID, company_id: UUID) -> ServiceDTO:
        service = await self.service_use_case.get_service(id, company_id)
        return ServiceSchema(**service.model_dump())

    async def update_service(
        self, id: UUID, service: UpdateServiceSchema, company_id: UUID
    ) -> ServiceSchema:
        service_dto = UpdateServiceDTO(**service.model_dump(exclude_unset=True))
        updated_service = await self.service_use_case.update_service(
            id, service_dto, company_id
        )
        return ServiceSchema(**updated_service.model_dump())

    async def delete_service(self, id: UUID, company_id: UUID) -> bool:
        return await self.service_use_case.delete_service(id, company_id)

    async def upload_service_image(
        self, *, file: UploadFile, company_id: UUID
    ) -> UploadServiceImageOutSchema:
        result = await self.storage.upload_service_image(
            file=file, company_id=company_id
        )
        return UploadServiceImageOutSchema(url=result.url)
