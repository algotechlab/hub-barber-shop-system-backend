from uuid import UUID, uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.service import CreateServiceDTO, ServiceDTO, UpdateServiceDTO
from src.domain.repositories.service import ServiceRepository


@pytest.mark.unit
class TestServiceRepositoryContract:
    def test_service_repository_exposes_contract_methods(self):
        assert hasattr(ServiceRepository, 'create_service')
        assert hasattr(ServiceRepository, 'get_service')
        assert hasattr(ServiceRepository, 'list_services')
        assert hasattr(ServiceRepository, 'update_service')
        assert hasattr(ServiceRepository, 'delete_service')

        assert getattr(ServiceRepository.create_service, '__isabstractmethod__', False)
        assert getattr(ServiceRepository.get_service, '__isabstractmethod__', False)
        assert getattr(ServiceRepository.list_services, '__isabstractmethod__', False)
        assert getattr(ServiceRepository.update_service, '__isabstractmethod__', False)
        assert getattr(ServiceRepository.delete_service, '__isabstractmethod__', False)

    async def test_can_implement_concrete_repository(self):
        company_id = uuid4()
        service_id = uuid4()

        create = CreateServiceDTO(
            name='Corte',
            description='Desc',
            price='10',
            duration=30,
            category='Cat',
            time_to_spend=30,
            status=True,
            url_image='https://cdn.example.com/a.png',
            company_id=company_id,
        )

        out = ServiceDTO(
            id=service_id,
            name=create.name,
            description=create.description,
            price=create.price,
            duration=create.duration,
            category=create.category,
            time_to_spend=create.time_to_spend,
            status=create.status,
            url_image=create.url_image,
            company_id=company_id,
        )

        class ConcreteServiceRepository(ServiceRepository):
            async def create_service(self, service: CreateServiceDTO) -> ServiceDTO:
                return out

            async def get_service(
                self, id: UUID, company_id: UUID
            ) -> ServiceDTO | None:
                return (
                    out if (id == service_id and company_id == out.company_id) else None
                )

            async def list_services(
                self, pagination: PaginationParamsDTO, company_id: UUID
            ) -> list[ServiceDTO]:
                return [out]

            async def update_service(
                self, id: UUID, service: UpdateServiceDTO, company_id: UUID
            ) -> ServiceDTO | None:
                return out if id == service_id else None

            async def delete_service(self, id: UUID, company_id: UUID) -> bool:
                return id == service_id

        repo = ConcreteServiceRepository()
        assert await repo.list_services(PaginationParamsDTO(), company_id) == [out]
        assert await repo.create_service(create) == out
        assert await repo.get_service(service_id, company_id) == out
        assert (
            await repo.update_service(
                service_id, UpdateServiceDTO(name='X'), company_id
            )
            == out
        )
        assert await repo.delete_service(service_id, company_id) is True
