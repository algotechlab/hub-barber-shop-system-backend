from typing import List, Optional
from uuid import UUID

from src.core.utils.get_argon import hash_password
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.owner import CreateOwnerDTO, OwnerOutDTO, UpdateOwnerDTO
from src.domain.execptions.owner import (
    OwnerAlreadyExistsException,
    OwnerNotFoundException,
)
from src.domain.service.owner import OwnerService


class OwnerUseCase:
    def __init__(self, owner_service: OwnerService):
        self.owner_service = owner_service

    async def create_owner(self, owner: CreateOwnerDTO) -> OwnerOutDTO:
        if await self.owner_service.get_owner_by_email(owner.email):
            raise OwnerAlreadyExistsException('Proprietário já existe')

        owner_dto = CreateOwnerDTO(
            name=owner.name,
            email=owner.email,
            password=hash_password(owner.password),
            phone=owner.phone,
        )
        created_owner = await self.owner_service.create_owner(owner_dto)
        return OwnerOutDTO(**created_owner.model_dump())

    async def get_owner(self, id: UUID) -> Optional[OwnerOutDTO]:
        owner = await self.owner_service.get_owner(id)
        if not owner:
            raise OwnerNotFoundException('Proprietário não encontrado')
        return OwnerOutDTO(**owner.model_dump())

    async def update_owner(
        self, id: UUID, owner: UpdateOwnerDTO
    ) -> Optional[OwnerOutDTO]:
        update_data = owner.model_dump(exclude_none=True)
        if 'password' in update_data:
            update_data['password'] = hash_password(update_data['password'])

        owner_dto = UpdateOwnerDTO(**update_data)
        if not await self.owner_service.get_owner(id):
            raise OwnerNotFoundException('Proprietário não encontrado')
        updated_owner = await self.owner_service.update_owner(id, owner_dto)
        return OwnerOutDTO(**updated_owner.model_dump()) if updated_owner else None

    async def delete_owner(self, id: UUID) -> None:
        if not await self.owner_service.get_owner(id):
            raise OwnerNotFoundException('Proprietário não encontrado')
        return await self.owner_service.delete_owner(id)

    async def list_owners(self, pagination: PaginationParamsDTO) -> List[OwnerOutDTO]:
        return await self.owner_service.list_owners(pagination)
