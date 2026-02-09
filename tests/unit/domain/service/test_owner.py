from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.owner import CreateOwnerDTO, OwnerOutDTO, UpdateOwnerDTO
from src.domain.service.owner import OwnerService


@pytest.mark.unit
class TestOwnerService:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository):
        return OwnerService(owner_repository=mock_repository)

    async def test_list_owners_delegates_to_repository(self, service, mock_repository):
        pagination = PaginationParamsDTO()
        expected = []
        mock_repository.list_owners.return_value = expected

        result = await service.list_owners(pagination)

        mock_repository.list_owners.assert_awaited_once_with(pagination)
        assert result == expected

    async def test_create_owner_delegates_to_repository(self, service, mock_repository):
        owner_dto = CreateOwnerDTO(
            name='John',
            email='john@example.com',
            password='plain',
            phone='11999999999',
        )
        expected = OwnerOutDTO(
            id=uuid4(),
            name=owner_dto.name,
            email=owner_dto.email,
            phone=owner_dto.phone,
            created_at=datetime.now(timezone.utc),
        )
        mock_repository.create_owner.return_value = expected

        result = await service.create_owner(owner_dto)

        mock_repository.create_owner.assert_awaited_once_with(owner_dto)
        assert result == expected

    async def test_get_owner_delegates_to_repository(self, service, mock_repository):
        owner_id = uuid4()
        mock_repository.get_owner.return_value = None

        result = await service.get_owner(owner_id)

        mock_repository.get_owner.assert_awaited_once_with(owner_id)
        assert result is None

    async def test_get_owner_by_email_delegates_to_repository(
        self, service, mock_repository
    ):
        mock_repository.get_owner_by_email.return_value = None

        result = await service.get_owner_by_email('john@example.com')

        mock_repository.get_owner_by_email.assert_awaited_once_with('john@example.com')
        assert result is None

    async def test_update_owner_delegates_to_repository(self, service, mock_repository):
        owner_id = uuid4()
        update_dto = UpdateOwnerDTO(name='Updated')
        mock_repository.update_owner.return_value = None

        result = await service.update_owner(owner_id, update_dto)

        mock_repository.update_owner.assert_awaited_once_with(owner_id, update_dto)
        assert result is None

    async def test_delete_owner_delegates_to_repository(self, service, mock_repository):
        owner_id = uuid4()
        mock_repository.delete_owner.return_value = True

        result = await service.delete_owner(owner_id)

        mock_repository.delete_owner.assert_awaited_once_with(owner_id)
        assert result is True
