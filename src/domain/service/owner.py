from typing import List, Optional
from uuid import UUID

from src.domain.dtos.auth import OwnerAuthDTO
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.owner import CreateOwnerDTO, OwnerOutDTO, UpdateOwnerDTO
from src.domain.repositories.owner import OwnerRepository


class OwnerService:
    def __init__(self, owner_repository: OwnerRepository):
        self.owner_repository = owner_repository

    async def create_owner(self, owner: CreateOwnerDTO) -> OwnerOutDTO:
        return await self.owner_repository.create_owner(owner)

    async def get_owner(self, id: UUID) -> Optional[OwnerOutDTO]:
        return await self.owner_repository.get_owner(id)

    async def get_owner_by_email(self, email: str) -> Optional[OwnerOutDTO]:
        return await self.owner_repository.get_owner_by_email(email)

    async def get_owner_auth_by_email(self, email: str) -> Optional[OwnerAuthDTO]:
        return await self.owner_repository.get_owner_auth_by_email(email)

    async def update_owner(
        self, id: UUID, owner: UpdateOwnerDTO
    ) -> Optional[OwnerOutDTO]:
        return await self.owner_repository.update_owner(id, owner)

    async def delete_owner(self, id: UUID) -> None:
        return await self.owner_repository.delete_owner(id)

    async def list_owners(self, pagination: PaginationParamsDTO) -> List[OwnerOutDTO]:
        return await self.owner_repository.list_owners(pagination)
