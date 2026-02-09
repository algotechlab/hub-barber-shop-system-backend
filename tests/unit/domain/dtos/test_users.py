import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError
from src.domain.dtos.users import UpdateUserDTO, UserBaseDTO, UserOutDTO


@pytest.mark.unit
class TestUserBaseDTO:
    def test_create_valid_user_base_dto(self, generate_uuid, generate_model_user):
        user = generate_model_user
        dto = UserBaseDTO(
            name=user.name,
            email=user.email,
            password=user.password,
            company_id=generate_uuid,
        )
        assert dto.name == user.name
        assert dto.email == user.email
        assert dto.password == user.password
        assert dto.company_id == generate_uuid

    def test_user_base_dto_model_dump(self, generate_uuid, generate_model_user):
        user = generate_model_user
        dto = UserBaseDTO(
            name=user.name,
            email=user.email,
            password=user.password,
            company_id=generate_uuid,
        )
        data = dto.model_dump()
        assert data['name'] == user.name
        assert data['email'] == user.email
        assert data['password'] == user.password
        assert data['company_id'] == generate_uuid

    def test_user_base_dto_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            UserBaseDTO(
                name='Test',
                email='test@example.com',
            )


@pytest.mark.unit
class TestUpdateUserDTO:
    def test_create_empty_update_dto(self):
        dto = UpdateUserDTO()
        assert dto.name is None
        assert dto.email is None
        assert dto.password is None
        assert dto.is_active is None

    def test_create_partial_update_dto(self):
        dto = UpdateUserDTO(name='Novo Nome', is_active=False)
        assert dto.name == 'Novo Nome'
        assert dto.is_active is False
        assert dto.email is None
        assert dto.password is None

    def test_update_dto_exclude_unset(self):
        dto = UpdateUserDTO(name='John Doe')
        dumped = dto.model_dump(exclude_unset=True)
        assert 'name' in dumped
        assert dumped['name'] == 'John Doe'
        assert 'email' not in dumped or dumped.get('email') is None


@pytest.mark.unit
class TestUserOutDTO:
    def test_create_user_out_dto_from_attributes(
        self, generate_uuid, generate_model_user
    ):
        user = generate_model_user
        company_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        dto = UserOutDTO(
            id=generate_uuid,
            name=user.name,
            email=user.email,
            password=user.password,
            company_id=company_id,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        assert dto.id == generate_uuid
        assert dto.name == user.name
        assert dto.email == user.email
        assert dto.is_active is True
        assert dto.created_at == now
        assert dto.updated_at == now

    def test_user_out_dto_inherits_base_fields(
        self, generate_uuid, generate_model_user
    ):
        user = generate_model_user
        company_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        dto = UserOutDTO(
            id=generate_uuid,
            name=user.name,
            email=user.email,
            password=user.password,
            company_id=company_id,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        assert isinstance(dto, UserBaseDTO)
        assert dto.model_config.get('from_attributes') is True
