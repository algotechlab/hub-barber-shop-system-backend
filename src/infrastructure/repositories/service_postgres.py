from datetime import timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.service import CreateServiceDTO, ServiceDTO, UpdateServiceDTO
from src.domain.repositories.service import ServiceRepository
from src.infrastructure.database.models.service import Service


class ServiceRepositoryPostgres(ServiceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_service(self, service: CreateServiceDTO) -> ServiceDTO:
        try:
            data = service.model_dump()
            if isinstance(data.get('time_to_spend'), int):
                data['time_to_spend'] = timedelta(minutes=data['time_to_spend'])

            service = Service(**data)
            self.session.add(service)
            await self.session.commit()
            await self.session.refresh(service)
            return ServiceDTO.model_validate(service)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_service(self, id: UUID, company_id: UUID) -> Optional[ServiceDTO]:
        try:
            query = select(Service).where(
                Service.id.__eq__(id),
                Service.company_id.__eq__(company_id),
                Service.is_deleted.__eq__(False),
            )
            result = await self.session.execute(query)
            service = result.scalar_one_or_none()
            if service is None:
                return None
            return ServiceDTO.model_validate(service)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def list_services(
        self, pagination: PaginationParamsDTO, company_id: UUID
    ) -> List[ServiceDTO]:
        try:
            query = (
                select(Service)
                .where(
                    Service.company_id.__eq__(company_id),
                    Service.is_deleted.__eq__(False),
                )
                .order_by(Service.created_at.desc())
            )

            if pagination.filter_by and pagination.filter_value:
                query = query.filter(
                    getattr(Service, pagination.filter_by).ilike(
                        f'%{pagination.filter_value}%'
                    )
                )

            query = query.offset(pagination.offset).limit(pagination.limit)
            result = await self.session.execute(query)
            services = result.scalars().all()
            return [ServiceDTO.model_validate(service) for service in services]
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def update_service(
        self, id: UUID, service: UpdateServiceDTO, company_id: UUID
    ) -> Optional[ServiceDTO]:
        try:
            update_data = service.model_dump(exclude_unset=True, exclude_none=True)
            if isinstance(update_data.get('time_to_spend'), int):
                update_data['time_to_spend'] = timedelta(
                    minutes=update_data['time_to_spend']
                )
            query = (
                update(Service)
                .where(
                    Service.id.__eq__(id),
                    Service.company_id.__eq__(company_id),
                    Service.is_deleted.__eq__(False),
                )
                .values(**update_data)
                .returning(Service)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            updated = result.scalar_one_or_none()
            if updated is None:
                return None
            return ServiceDTO.model_validate(updated)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def delete_service(self, id: UUID, company_id: UUID) -> bool:
        try:
            stmt = (
                update(Service)
                .where(
                    Service.id.__eq__(id),
                    Service.company_id.__eq__(company_id),
                    Service.is_deleted.__eq__(False),
                )
                .values(is_deleted=True)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
