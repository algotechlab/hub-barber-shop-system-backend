from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError
from src.domain.dtos.users import UserBaseDTO, UserOutDTO
from src.interface.api.v1.schema.users import (
    CreateUserSchema,
    UpdateUserSchema,
    UserOutSchema,
    UserSchema,
)


@pytest.mark.unit
class TestUserSchema:
    def test_valid_user_schema(
        self, generate_uuid: UUID, generate_user_out_dto: UserOutDTO
    ):
        schema = UserSchema(**generate_user_out_dto.model_dump())
        assert schema.id == generate_user_out_dto.id
        assert schema.name == generate_user_out_dto.name
        assert schema.email == generate_user_out_dto.email
        assert schema.is_active is generate_user_out_dto.is_active

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            UserSchema(
                id=uuid4(),
                name='Test',
                email='test@example.com',
                # password, is_active, company_id missing
            )


@pytest.mark.unit
class TestCreateUserSchema:
    def test_valid_create_schema(
        self, generate_uuid: UUID, generate_user_base_dto: UserBaseDTO
    ):
        schema = CreateUserSchema(
            name=generate_user_base_dto.name,
            email=generate_user_base_dto.email,
            phone=generate_user_base_dto.phone,
            password=generate_user_base_dto.password,
            company_id=generate_uuid,
        )
        assert schema.name == generate_user_base_dto.name
        assert schema.email == generate_user_base_dto.email
        assert schema.company_id == generate_uuid

    def test_model_dump_for_dto(
        self, generate_uuid: UUID, generate_user_base_dto: UserBaseDTO
    ):
        schema = CreateUserSchema(
            name=generate_user_base_dto.name,
            email=generate_user_base_dto.email,
            phone=generate_user_base_dto.phone,
            password=generate_user_base_dto.password,
            company_id=generate_uuid,
        )
        data = schema.model_dump()
        assert data['company_id'] == generate_uuid
        assert 'name' in data


@pytest.mark.unit
class TestUpdateUserSchema:
    def test_empty_update_schema(self):
        schema = UpdateUserSchema()
        assert schema.name is None
        assert schema.email is None
        assert schema.is_active is None

    def test_partial_update_schema(self, generate_user_base_dto: UserBaseDTO):
        schema = UpdateUserSchema(name=generate_user_base_dto.name, is_active=False)
        assert schema.name == generate_user_base_dto.name
        assert schema.is_active is False

    def test_exclude_none_for_patch(self, generate_user_base_dto: UserBaseDTO):
        schema = UpdateUserSchema(name=generate_user_base_dto.name)
        dumped = schema.model_dump(exclude_none=True)
        assert dumped == {'name': generate_user_base_dto.name}


@pytest.mark.unit
class TestUserOutSchema:
    def test_valid_user_out_schema(
        self, generate_uuid: UUID, generate_user_out_dto: UserOutDTO
    ):
        schema = UserOutSchema(
            id=generate_user_out_dto.id,
            name=generate_user_out_dto.name,
            email=generate_user_out_dto.email,
            password=generate_user_out_dto.password,
            is_active=generate_user_out_dto.is_active,
            company_id=generate_uuid,
        )
        assert schema.id == generate_user_out_dto.id
        assert schema.name == generate_user_out_dto.name
        assert schema.email == generate_user_out_dto.email
        assert schema.password == generate_user_out_dto.password
        assert schema.is_active == generate_user_out_dto.is_active
        assert schema.company_id == generate_uuid
