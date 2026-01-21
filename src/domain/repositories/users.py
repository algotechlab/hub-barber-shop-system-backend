from abc import abstractmethod
from typing import Optional
from uuid import UUID

from src.application.dtos.common.pagination import PaginationParamsDTO
from src.application.dtos.users import UpdateUserDTO, UserBaseDTO, UserOutDTO


class UsersRepository:
    @abstractmethod
    async def list_users(self, pagination: PaginationParamsDTO) -> list[UserOutDTO]: ...

    @abstractmethod
    async def get_user(self, id: UUID) -> Optional[UserOutDTO]: ...

    @abstractmethod
    async def create_user(self, user: UserBaseDTO) -> UserOutDTO: ...

    @abstractmethod
    async def update_user(
        self, id: UUID, user: UpdateUserDTO
    ) -> Optional[UserOutDTO]: ...

    @abstractmethod
    async def delete_user(self, id: UUID) -> Optional[bool]: ...
