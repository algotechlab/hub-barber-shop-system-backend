from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.users import UpdateUserDTO, UserBaseDTO
from src.domain.use_case.users import UsersUseCase

PLAIN_PASSWORD = 'password'
HASHED_PASSWORD = 'hashed_argon2'


@pytest.mark.unit
class TestUsersUseCase:
    @pytest.fixture
    def mock_service(self):
        return AsyncMock()

    @pytest.fixture
    def users_use_case(self, mock_service):
        return UsersUseCase(users_service=mock_service)

    async def test_list_users_delegates_to_service(self, users_use_case, mock_service):
        pagination = PaginationParamsDTO()
        expected = []
        mock_service.list_users.return_value = expected

        result = await users_use_case.list_users(pagination)

        mock_service.list_users.assert_awaited_once_with(pagination)
        assert result == expected

    async def test_get_user_delegates_to_service(
        self, users_use_case, mock_service, generate_uuid, generate_user_out_dto
    ):
        user_id = generate_uuid
        mock_service.get_user.return_value = generate_user_out_dto

        result = await users_use_case.get_user(user_id)

        mock_service.get_user.assert_awaited_once_with(user_id)
        assert result is not None
        assert result.model_dump() == generate_user_out_dto.model_dump()

    @patch('src.domain.use_case.users.hash_password')
    async def test_create_user_hashes_password_before_create(
        self,
        mock_hash_password,
        users_use_case,
        mock_service,
        generate_uuid,
        generate_user_out_dto,
    ):
        user_base_dto = UserBaseDTO(
            name='John Doe',
            email='john.doe@example.com',
            password=PLAIN_PASSWORD,
            company_id=generate_uuid,
        )
        mock_hash_password.return_value = HASHED_PASSWORD
        mock_service.create_user.return_value = generate_user_out_dto

        result = await users_use_case.create_user(user_base_dto)

        mock_hash_password.assert_called_once_with(PLAIN_PASSWORD)
        dto_enviado_ao_service = mock_service.create_user.call_args[0][0]
        assert dto_enviado_ao_service.password == HASHED_PASSWORD
        assert result.model_dump() == generate_user_out_dto.model_dump()

    async def test_update_user_delegates_to_service(
        self, users_use_case, mock_service, generate_uuid, generate_user_out_dto
    ):
        user_id = generate_uuid
        update_dto = UpdateUserDTO(name='Updated Name')
        mock_service.update_user.return_value = generate_user_out_dto

        result = await users_use_case.update_user(user_id, update_dto)

        mock_service.update_user.assert_awaited_once_with(user_id, update_dto)
        assert result is not None
        assert result.model_dump() == generate_user_out_dto.model_dump()

    async def test_delete_user_delegates_to_service(self, users_use_case, mock_service):
        user_id = uuid4()
        mock_service.delete_user.return_value = True

        result = await users_use_case.delete_user(user_id)

        mock_service.delete_user.assert_awaited_once_with(user_id)
        assert result is True
