from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError
from src.domain.dtos.auth import OwnerAuthDTO
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.owner import CreateOwnerDTO, OwnerOutDTO, UpdateOwnerDTO
from src.domain.repositories.owner import OwnerRepository


@pytest.mark.unit
class TestOwnerRepositoryContract:
    def test_owner_repository_exposes_contract_methods(self):
        assert hasattr(OwnerRepository, 'list_owners')
        assert hasattr(OwnerRepository, 'create_owner')
        assert hasattr(OwnerRepository, 'get_owner')
        assert hasattr(OwnerRepository, 'get_owner_by_email')
        assert hasattr(OwnerRepository, 'get_owner_auth_by_email')
        assert hasattr(OwnerRepository, 'update_owner')
        assert hasattr(OwnerRepository, 'delete_owner')

        assert getattr(OwnerRepository.list_owners, '__isabstractmethod__', False)
        assert getattr(OwnerRepository.create_owner, '__isabstractmethod__', False)
        assert getattr(OwnerRepository.get_owner, '__isabstractmethod__', False)
        assert getattr(
            OwnerRepository.get_owner_by_email, '__isabstractmethod__', False
        )
        assert getattr(
            OwnerRepository.get_owner_auth_by_email, '__isabstractmethod__', False
        )
        assert getattr(OwnerRepository.update_owner, '__isabstractmethod__', False)
        assert getattr(OwnerRepository.delete_owner, '__isabstractmethod__', False)

    async def test_can_implement_concrete_repository(self):
        now = datetime.now(timezone.utc)
        owner_id = uuid4()

        base = CreateOwnerDTO(
            name='John',
            email='john@example.com',
            password='plain',
            phone='11999999999',
        )
        out = OwnerOutDTO(
            id=owner_id,
            name=base.name,
            email=base.email,
            phone=base.phone,
            created_at=now,
        )

        class ConcreteOwnerRepository(OwnerRepository):
            async def list_owners(
                self, pagination: PaginationParamsDTO
            ) -> list[OwnerOutDTO]:
                return [out]

            async def create_owner(self, owner: CreateOwnerDTO) -> OwnerOutDTO:
                return out

            async def get_owner(self, id: UUID) -> OwnerOutDTO | None:
                return out if id == owner_id else None

            async def get_owner_by_email(self, email: str) -> OwnerOutDTO | None:
                return out if email == base.email else None

            async def get_owner_auth_by_email(self, email: str) -> OwnerAuthDTO | None:
                if email != base.email:
                    return None
                return OwnerAuthDTO(id=owner_id, password='hashed')

            async def update_owner(
                self, id: UUID, owner: UpdateOwnerDTO
            ) -> OwnerOutDTO | None:
                return out if id == owner_id else None

            async def delete_owner(self, id: UUID) -> bool | None:
                return id == owner_id

        repo = ConcreteOwnerRepository()
        result_list = await repo.list_owners(PaginationParamsDTO())
        assert result_list == [out]

        created = await repo.create_owner(base)
        assert created == out

        found = await repo.get_owner(owner_id)
        assert found == out

        found_by_email = await repo.get_owner_by_email(base.email)
        assert found_by_email == out

        updated = await repo.update_owner(owner_id, UpdateOwnerDTO(name='X'))
        assert updated == out

        deleted = await repo.delete_owner(owner_id)
        assert deleted is True

    def test_filters_are_validated_by_pagination_dto(self):
        with pytest.raises(ValidationError):
            PaginationParamsDTO(filter_by='email', filter_value='x')
