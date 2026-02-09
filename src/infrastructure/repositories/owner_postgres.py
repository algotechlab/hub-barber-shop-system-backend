from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.owner import CreateOwnerDTO, OwnerOutDTO, UpdateOwnerDTO
from src.domain.repositories.owner import OwnerRepository
from src.infrastructure.database.models.owner import Owner


class OwnerRepositoryPostgres(OwnerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_owner(self, owner: CreateOwnerDTO) -> OwnerOutDTO:
        try:
            owner = Owner(**owner.model_dump())
            self.session.add(owner)
            await self.session.commit()
            await self.session.refresh(owner)
            return OwnerOutDTO.model_validate(owner)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_owner(self, id: UUID) -> Optional[OwnerOutDTO]:
        try:
            query = select(Owner).where(
                Owner.id.__eq__(id), Owner.is_deleted.__eq__(False)
            )
            result = await self.session.execute(query)
            owner = result.scalar_one_or_none()
            if owner is None:
                return None
            return OwnerOutDTO.model_validate(owner)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_owner_by_email(self, email: str) -> Optional[OwnerOutDTO]:
        try:
            query = select(Owner).where(
                Owner.email.__eq__(email), Owner.is_deleted.__eq__(False)
            )
            result = await self.session.execute(query)
            owner = result.scalar_one_or_none()
            if owner is None:
                return None
            return OwnerOutDTO.model_validate(owner)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def list_owners(self, pagination: PaginationParamsDTO) -> List[OwnerOutDTO]:
        try:
            query = (
                select(Owner)
                .where(Owner.is_deleted.__eq__(False))
                .order_by(Owner.created_at.desc())
            )

            if pagination.filter_by and pagination.filter_value:
                query = query.filter(
                    getattr(Owner, pagination.filter_by).ilike(
                        f'%{pagination.filter_value}%'
                    )
                )

            result = await self.session.execute(query)
            owners = result.scalars().all()
            return [OwnerOutDTO.model_validate(owner) for owner in owners]
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def update_owner(
        self, id: UUID, owner: UpdateOwnerDTO
    ) -> Optional[OwnerOutDTO]:
        try:
            update_data = owner.model_dump(exclude_unset=True, exclude_none=True)
            query = (
                update(Owner)
                .where(Owner.id.__eq__(id), Owner.is_deleted.__eq__(False))
                .values(**update_data)
                .returning(Owner)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            updated_owner = result.scalar_one_or_none()
            if updated_owner is None:
                return None
            return OwnerOutDTO.model_validate(updated_owner)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def delete_owner(self, id: UUID) -> None:
        try:
            stmt = (
                update(Owner)
                .where(Owner.id.__eq__(id), Owner.is_deleted.__eq__(False))
                .values(is_deleted=True)
                .returning(Owner)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()

            updated_owner = result.scalar_one_or_none()

            return updated_owner is not None
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
