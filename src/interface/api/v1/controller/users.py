from typing import List, Optional
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.users import UpdateUserDTO, UserBaseDTO
from src.domain.use_case.users import UsersUseCase
from src.interface.api.v1.schema.users import (
    CreateUserSchema,
    UpdateUserSchema,
    UserOutSchema,
    UserSchema,
)


class UsersController:
    def __init__(self, users_use_case: UsersUseCase):
        self.users_use_case = users_use_case

    async def list_users(self, pagination: PaginationParamsDTO) -> List[UserSchema]:
        users = await self.users_use_case.list_users(pagination)
        return [UserSchema(**user.model_dump()) for user in users]

    async def get_user(self, id: UUID) -> Optional[UserSchema]:
        user = await self.users_use_case.get_user(id)
        if user is None:
            return None
        return UserSchema(**user.model_dump())

    async def create_user(self, user: CreateUserSchema) -> UserSchema:
        user_dto = UserBaseDTO(**user.model_dump())
        created_user = await self.users_use_case.create_user(user_dto)
        return UserSchema(**created_user.model_dump())

    async def update_user(
        self, id: UUID, user: UpdateUserSchema
    ) -> Optional[UserOutSchema]:
        user_dto = UpdateUserDTO(**user.model_dump(exclude_none=True))
        user = await self.users_use_case.update_user(id, user_dto)
        return UserSchema(**user.model_dump()) if user else None

    async def delete_user(self, id: UUID) -> Optional[bool]:
        return await self.users_use_case.delete_user(id)
