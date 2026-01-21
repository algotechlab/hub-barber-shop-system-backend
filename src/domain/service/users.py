from typing import Optional
from uuid import UUID

from src.application.dtos.common.pagination import PaginationParamsDTO
from src.application.dtos.users import UpdateUserDTO, UserBaseDTO, UserOutDTO
from src.domain.repositories.users import UsersRepository


class UsersService:
    def __init__(self, users_repository: UsersRepository):
        self.users_repository = users_repository

    async def list_users(self, pagination: PaginationParamsDTO) -> list[UserOutDTO]:
        return await self.users_repository.list_users(pagination)

    async def get_user(self, id: UUID) -> Optional[UserOutDTO]:
        return await self.users_repository.get_user(id)

    async def create_user(self, user: UserBaseDTO) -> UserOutDTO:
        return await self.users_repository.create_user(user)

    async def update_user(self, id: UUID, user: UpdateUserDTO) -> Optional[UserOutDTO]:
        return await self.users_repository.update_user(id, user)

    async def delete_user(self, id: UUID) -> Optional[bool]:
        return await self.users_repository.delete_user(id)
