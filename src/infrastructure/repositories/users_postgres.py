from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.auth import UserAuthDTO
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.users import UpdateUserDTO, UserBaseDTO, UserOutDTO
from src.domain.repositories.users import UsersRepository
from src.infrastructure.database.models.users import User


class UsersRepositoryPostgres(UsersRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_data: UserBaseDTO) -> UserOutDTO:
        try:
            user = User(**user_data.model_dump())
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return UserOutDTO.model_validate(user)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_user(self, user_id: UUID) -> Optional[UserOutDTO]:
        try:
            query = select(User).where(
                User.id.__eq__(user_id), User.is_deleted.__eq__(False)
            )
            result = await self.session.execute(query)
            user = result.scalar_one_or_none()

            if user is None:
                return None

            return UserOutDTO.model_validate(user)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_user_auth_by_phone(self, phone: str) -> Optional[UserAuthDTO]:
        try:
            query = select(User).where(
                User.phone.__eq__(phone), User.is_deleted.__eq__(False)
            )
            result = await self.session.execute(query)
            user = result.scalar_one_or_none()
            if user is None:
                return None
            return UserAuthDTO.model_validate(user)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def list_users(self, pagination: PaginationParamsDTO) -> List[UserOutDTO]:
        try:
            query = (
                select(User)
                .where(User.is_deleted.__eq__(False))
                .order_by(User.created_at)
            )

            if pagination.filter_by and pagination.filter_value:
                query = query.filter(
                    getattr(User, pagination.filter_by).__eq__(pagination.filter_value)
                )
            result = await self.session.execute(query)
            users = result.scalars().all()
            return [UserOutDTO.model_validate(user) for user in users]
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def update_user(
        self, user_id: UUID, user_update: UpdateUserDTO
    ) -> Optional[UserOutDTO]:
        try:
            update_data = user_update.model_dump(exclude_unset=True, exclude_none=True)

            stmt = (
                update(User)
                .where(User.id.__eq__(user_id))
                .values(**update_data)
                .returning(User)
            )

            result = await self.session.execute(stmt)
            await self.session.commit()

            updated_user = result.scalar_one_or_none()

            if updated_user is None:
                return None

            return UserOutDTO.model_validate(updated_user)

        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def delete_user(self, user_id: UUID) -> bool:
        try:
            stmt = (
                update(User)
                .where(User.id.__eq__(user_id), User.is_deleted.__eq__(False))
                .values(is_deleted=True)
                .returning(User)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()

            updated_user = result.scalar_one_or_none()

            return updated_user is not None
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
