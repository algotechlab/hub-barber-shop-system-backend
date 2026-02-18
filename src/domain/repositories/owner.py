from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.dtos.auth import OwnerAuthDTO
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.owner import CreateOwnerDTO, OwnerOutDTO, UpdateOwnerDTO


class OwnerRepository:
    @abstractmethod
    async def create_owner(self, owner: CreateOwnerDTO) -> OwnerOutDTO: ...

    @abstractmethod
    async def get_owner(self, id: UUID) -> Optional[OwnerOutDTO]: ...

    @abstractmethod
    async def get_owner_by_email(self, email: str) -> Optional[OwnerOutDTO]: ...

    @abstractmethod
    async def get_owner_auth_by_email(self, email: str) -> Optional[OwnerAuthDTO]: ...

    @abstractmethod
    async def update_owner(
        self, id: UUID, owner: UpdateOwnerDTO
    ) -> Optional[OwnerOutDTO]: ...

    @abstractmethod
    async def delete_owner(self, id: UUID) -> None: ...

    @abstractmethod
    async def list_owners(
        self, pagination: PaginationParamsDTO
    ) -> List[OwnerOutDTO]: ...
