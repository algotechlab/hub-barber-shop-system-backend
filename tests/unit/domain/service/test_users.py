import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.users import UpdateUserDTO, UserBaseDTO
from src.domain.service.users import UsersService


@pytest.mark.unit
class TestUsersService:
    @pytest.fixture
    def users_service(self, mock_repository_user):
        return UsersService(users_repository=mock_repository_user)

    async def test_list_users_delegates_to_repository(
        self, users_service, mock_repository_user
    ):
        pagination = PaginationParamsDTO()
        expected = []
        mock_repository_user.list_users.return_value = expected

        result = await users_service.list_users(pagination)

        mock_repository_user.list_users.assert_awaited_once_with(pagination)
        assert result == expected

    async def test_get_user_delegates_to_repository(
        self, users_service, mock_repository_user, generate_uuid, generate_model_user
    ):
        user_id = generate_uuid
        out_dto = generate_model_user
        mock_repository_user.get_user.return_value = out_dto

        result = await users_service.get_user(user_id)

        mock_repository_user.get_user.assert_awaited_once_with(user_id)
        assert result == out_dto

    async def test_get_user_returns_none_when_not_found(
        self, users_service, mock_repository_user, generate_uuid
    ):
        user_id = generate_uuid
        mock_repository_user.get_user.return_value = None

        result = await users_service.get_user(user_id)

        assert result is None

    async def test_create_user_delegates_to_repository(
        self, users_service, mock_repository_user, generate_uuid, generate_model_user
    ):
        company_id = generate_uuid
        user = generate_model_user
        user_dto = UserBaseDTO(
            name=user.name,
            email=user.email,
            password=user.password,
            company_id=company_id,
        )
        mock_repository_user.create_user.return_value = user_dto

        result = await users_service.create_user(user_dto)

        mock_repository_user.create_user.assert_awaited_once_with(user_dto)
        assert result == user_dto

    async def test_update_user_delegates_to_repository(
        self, users_service, mock_repository_user, generate_uuid, generate_model_user
    ):
        user_id = generate_uuid
        user = generate_model_user
        update_dto = UpdateUserDTO(
            name=user.name,
            email=user.email,
            password=user.password,
        )
        mock_repository_user.update_user.return_value = user

        result = await users_service.update_user(user_id, update_dto)

        mock_repository_user.update_user.assert_awaited_once_with(user_id, update_dto)
        assert result == user

    async def test_delete_user_delegates_to_repository(
        self, users_service, mock_repository_user, generate_uuid
    ):
        user_id = generate_uuid
        mock_repository_user.delete_user.return_value = True

        result = await users_service.delete_user(user_id)

        mock_repository_user.delete_user.assert_awaited_once_with(user_id)
        assert result is True
