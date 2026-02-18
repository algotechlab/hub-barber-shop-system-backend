from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.users import UpdateUserDTO, UserOutDTO
from src.interface.api.v1.controller.users import UsersController
from src.interface.api.v1.schema.common.pagination import PaginationParamsBaseSchema
from src.interface.api.v1.schema.users import (
    CreateUserSchema,
    UpdateUserSchema,
    UserSchema,
)


@pytest.mark.unit
class TestUsersController:
    @pytest.fixture
    def mock_use_case(self):
        return AsyncMock()

    @pytest.fixture
    def controller(self, mock_use_case):
        return UsersController(users_use_case=mock_use_case)

    async def test_list_users_returns_schema_list(
        self, controller, mock_use_case, generate_uuid, generate_model_user
    ):
        user = generate_model_user
        company_id = generate_uuid
        now = datetime.now(timezone.utc)
        dto_list = [
            UserOutDTO(
                id=generate_uuid,
                name=user.name,
                email=user.email,
                password=user.password,
                phone=user.phone,
                company_id=company_id,
                is_active=True,
                created_at=now,
                updated_at=now,
            ),
        ]
        mock_use_case.list_users.return_value = dto_list
        pagination = PaginationParamsBaseSchema()

        result = await controller.list_users(pagination)

        mock_use_case.list_users.assert_awaited_once_with(pagination)
        assert len(result) == 1
        assert isinstance(result[0], UserSchema)
        assert result[0].name == user.name
        assert result[0].email == user.email

    async def test_get_user_returns_schema_when_found(
        self, controller, mock_use_case, generate_uuid, generate_model_user
    ):
        user = generate_model_user
        company_id = generate_uuid
        now = datetime.now(timezone.utc)
        out_dto = UserOutDTO(
            id=generate_uuid,
            name=user.name,
            email=user.email,
            password=user.password,
            phone=user.phone,
            company_id=company_id,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        mock_use_case.get_user.return_value = out_dto

        result = await controller.get_user(generate_uuid)

        mock_use_case.get_user.assert_awaited_once_with(generate_uuid)
        assert result is not None
        assert result.name == user.name
        assert result.email == user.email

    async def test_get_user_returns_none_when_not_found(
        self, controller, mock_use_case
    ):
        mock_use_case.get_user.return_value = None

        result = await controller.get_user(uuid4())

        assert result is None

    async def test_create_user_returns_schema(self, controller, mock_use_case):
        company_id = uuid4()
        create_schema = CreateUserSchema(
            name='New',
            email='new@example.com',
            password='plain',
            phone='11999999999',
            company_id=company_id,
        )
        out_dto = UserOutDTO(
            id=uuid4(),
            name=create_schema.name,
            email=create_schema.email,
            password='hashed',
            phone=create_schema.phone,
            company_id=company_id,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_use_case.create_user.return_value = out_dto

        result = await controller.create_user(create_schema)

        assert result.name == create_schema.name
        assert result.email == create_schema.email
        mock_use_case.create_user.assert_awaited_once()

    async def test_update_user_returns_schema_when_found(
        self, controller, mock_use_case, generate_uuid, generate_model_user
    ):
        user = generate_model_user
        company_id = generate_uuid
        update_schema = UpdateUserSchema(name=user.name)
        out_dto = UserOutDTO(
            id=generate_uuid,
            name=user.name,
            email=user.email,
            password=user.password,
            phone=user.phone,
            company_id=company_id,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_use_case.update_user.return_value = out_dto

        result = await controller.update_user(generate_uuid, update_schema)

        assert result is not None
        assert result.name == user.name
        mock_use_case.update_user.assert_awaited_once()
        call_args = mock_use_case.update_user.call_args[0]
        assert call_args[0] == generate_uuid
        assert isinstance(call_args[1], UpdateUserDTO)
        assert call_args[1].name == user.name

    async def test_update_user_returns_none_when_not_found(
        self, controller, mock_use_case
    ):
        mock_use_case.update_user.return_value = None

        result = await controller.update_user(uuid4(), UpdateUserSchema(name='X'))

        assert result is None

    async def test_delete_user_returns_bool(self, controller, mock_use_case):
        user_id = uuid4()
        mock_use_case.delete_user.return_value = True

        result = await controller.delete_user(user_id)

        mock_use_case.delete_user.assert_awaited_once_with(user_id)
        assert result is True
