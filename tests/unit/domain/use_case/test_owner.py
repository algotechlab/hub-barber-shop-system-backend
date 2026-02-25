from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.owner import CreateOwnerDTO, OwnerOutDTO, UpdateOwnerDTO
from src.domain.exceptions.owner import (
    OwnerAlreadyExistsException,
    OwnerNotFoundException,
)
from src.domain.use_case.owner import OwnerUseCase

PLAIN_PASSWORD = 'password'
HASHED_PASSWORD = 'hashed_argon2'


@pytest.mark.unit
class TestOwnerUseCase:
    @pytest.fixture
    def mock_service(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_service):
        return OwnerUseCase(owner_service=mock_service)

    @pytest.fixture
    def owner_create_dto(self):
        return CreateOwnerDTO(
            name='John',
            email='john@example.com',
            password=PLAIN_PASSWORD,
            phone='11999999999',
        )

    @pytest.fixture
    def owner_out_dto(self, owner_create_dto):
        return OwnerOutDTO(
            id=uuid4(),
            name=owner_create_dto.name,
            email=owner_create_dto.email,
            phone=owner_create_dto.phone,
            created_at=datetime.now(timezone.utc),
        )

    async def test_create_owner_raises_when_email_already_exists(
        self, use_case, mock_service, owner_create_dto, owner_out_dto
    ):
        mock_service.get_owner_by_email.return_value = owner_out_dto

        with pytest.raises(OwnerAlreadyExistsException, match='Proprietário já existe'):
            await use_case.create_owner(owner_create_dto)

        mock_service.get_owner_by_email.assert_awaited_once_with(owner_create_dto.email)

    @patch('src.domain.use_case.owner.hash_password')
    async def test_create_owner_hashes_password_and_delegates_to_service(
        self,
        mock_hash_password,
        use_case,
        mock_service,
        owner_create_dto,
        owner_out_dto,
    ):
        mock_hash_password.return_value = HASHED_PASSWORD
        mock_service.get_owner_by_email.return_value = None
        mock_service.create_owner.return_value = owner_out_dto

        result = await use_case.create_owner(owner_create_dto)

        mock_hash_password.assert_called_once_with(PLAIN_PASSWORD)
        dto_sent_to_service = mock_service.create_owner.call_args[0][0]
        assert dto_sent_to_service.password == HASHED_PASSWORD
        assert result.model_dump() == owner_out_dto.model_dump()

    async def test_get_owner_raises_when_not_found(self, use_case, mock_service):
        mock_service.get_owner.return_value = None

        with pytest.raises(OwnerNotFoundException, match='Proprietário não encontrado'):
            await use_case.get_owner(uuid4())

    async def test_get_owner_returns_owner_out_dto(
        self, use_case, mock_service, owner_out_dto
    ):
        owner_id = owner_out_dto.id
        mock_service.get_owner.return_value = owner_out_dto

        result = await use_case.get_owner(owner_id)

        mock_service.get_owner.assert_awaited_once_with(owner_id)
        assert result.model_dump() == owner_out_dto.model_dump()

    async def test_update_owner_raises_when_not_found(self, use_case, mock_service):
        mock_service.get_owner.return_value = None

        with pytest.raises(OwnerNotFoundException, match='Proprietário não encontrado'):
            await use_case.update_owner(uuid4(), UpdateOwnerDTO(name='X'))

    @patch('src.domain.use_case.owner.hash_password')
    async def test_update_owner_hashes_password_when_present(
        self, mock_hash_password, use_case, mock_service, owner_out_dto
    ):
        owner_id = owner_out_dto.id
        mock_hash_password.return_value = HASHED_PASSWORD
        mock_service.get_owner.return_value = owner_out_dto
        mock_service.update_owner.return_value = owner_out_dto

        result = await use_case.update_owner(owner_id, UpdateOwnerDTO(password='plain'))

        mock_hash_password.assert_called_once_with('plain')
        dto_sent_to_service = mock_service.update_owner.call_args[0][1]
        assert isinstance(dto_sent_to_service, UpdateOwnerDTO)
        assert dto_sent_to_service.password == HASHED_PASSWORD
        assert result.model_dump() == owner_out_dto.model_dump()

    @patch('src.domain.use_case.owner.hash_password')
    async def test_update_owner_does_not_hash_when_password_not_present(
        self, mock_hash_password, use_case, mock_service, owner_out_dto
    ):
        owner_id = owner_out_dto.id
        mock_service.get_owner.return_value = owner_out_dto
        mock_service.update_owner.return_value = owner_out_dto

        result = await use_case.update_owner(owner_id, UpdateOwnerDTO(name='Updated'))

        mock_hash_password.assert_not_called()
        assert result.model_dump() == owner_out_dto.model_dump()

    async def test_delete_owner_raises_when_not_found(self, use_case, mock_service):
        mock_service.get_owner.return_value = None

        with pytest.raises(OwnerNotFoundException, match='Proprietário não encontrado'):
            await use_case.delete_owner(uuid4())

    async def test_delete_owner_delegates_to_service_when_found(
        self, use_case, mock_service, owner_out_dto
    ):
        owner_id = owner_out_dto.id
        mock_service.get_owner.return_value = owner_out_dto
        mock_service.delete_owner.return_value = True

        result = await use_case.delete_owner(owner_id)

        mock_service.delete_owner.assert_awaited_once_with(owner_id)
        assert result is True

    async def test_list_owners_delegates_to_service(self, use_case, mock_service):
        pagination = PaginationParamsDTO()
        expected = []
        mock_service.list_owners.return_value = expected

        result = await use_case.list_owners(pagination)

        mock_service.list_owners.assert_awaited_once_with(pagination)
        assert result == expected
