from typing import Optional
from uuid import UUID

from src.core.utils.get_argon import hash_password
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.users import UpdateUserDTO, UserBaseDTO, UserOutDTO
from src.domain.service.users import UsersService


class UsersUseCase:
    def __init__(self, users_service: UsersService):
        self.users_service = users_service

    async def list_users(self, pagination: PaginationParamsDTO) -> list[UserOutDTO]:
        return await self.users_service.list_users(pagination)

    async def get_user(self, id: UUID) -> Optional[UserOutDTO]:
        return await self.users_service.get_user(id)

    async def create_user(self, user: UserBaseDTO) -> UserOutDTO:
        user.password = hash_password(user.password)
        return await self.users_service.create_user(user)

    async def update_user(self, id: UUID, user: UpdateUserDTO) -> Optional[UserOutDTO]:
        return await self.users_service.update_user(id, user)

    async def delete_user(self, id: UUID) -> Optional[bool]:
        return await self.users_service.delete_user(id)
