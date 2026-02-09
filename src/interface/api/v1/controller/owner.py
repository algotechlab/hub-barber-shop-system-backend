from typing import List, Optional
from uuid import UUID

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.owner import CreateOwnerDTO, UpdateOwnerDTO
from src.domain.use_case.owner import OwnerUseCase
from src.interface.api.v1.schema.owner import (
    CreateOwnerSchema,
    OwnerOutSchema,
    UpdateOwnerSchema,
)


class OwnerController:
    def __init__(self, owner_use_case: OwnerUseCase):
        self.owner_use_case = owner_use_case

    async def create_owner(self, owner: CreateOwnerSchema) -> OwnerOutSchema:
        owner_dto = CreateOwnerDTO(**owner.model_dump())
        created_owner = await self.owner_use_case.create_owner(owner_dto)
        return OwnerOutSchema(**created_owner.model_dump())

    async def get_owner(self, id: UUID) -> Optional[OwnerOutSchema]:
        owner = await self.owner_use_case.get_owner(id)
        if owner is None:
            return None
        return OwnerOutSchema(**owner.model_dump())

    async def update_owner(
        self, id: UUID, owner: UpdateOwnerSchema
    ) -> Optional[OwnerOutSchema]:
        owner_dto = UpdateOwnerDTO(**owner.model_dump(exclude_none=True))
        updated_owner = await self.owner_use_case.update_owner(id, owner_dto)
        return OwnerOutSchema(**updated_owner.model_dump()) if updated_owner else None

    async def delete_owner(self, id: UUID) -> None:
        return await self.owner_use_case.delete_owner(id)

    async def list_owners(
        self, pagination: PaginationParamsDTO
    ) -> List[OwnerOutSchema]:
        owners = await self.owner_use_case.list_owners(pagination)
        return [OwnerOutSchema(**owner.model_dump()) for owner in owners]
