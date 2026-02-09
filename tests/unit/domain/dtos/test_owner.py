from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.domain.dtos.owner import (
    CreateOwnerDTO,
    OwnerBaseDTO,
    OwnerOutDTO,
    UpdateOwnerDTO,
)


@pytest.mark.unit
class TestCreateOwnerDTO:
    def test_create_valid_create_owner_dto(self):
        dto = CreateOwnerDTO(
            name='John',
            email='john@example.com',
            password='plain',
            phone='11999999999',
        )
        assert dto.name == 'John'
        assert dto.email == 'john@example.com'
        assert dto.password == 'plain'
        assert dto.phone == '11999999999'

    def test_create_owner_dto_model_dump(self):
        dto = CreateOwnerDTO(
            name='Maria',
            email='maria@example.com',
            password='secret',
            phone='11988887777',
        )
        data = dto.model_dump()
        assert data['name'] == 'Maria'
        assert data['email'] == 'maria@example.com'
        assert data['password'] == 'secret'
        assert data['phone'] == '11988887777'

    def test_create_owner_dto_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            CreateOwnerDTO(
                name='John',
                # email missing
                password='plain',
                phone='11999999999',
            )


@pytest.mark.unit
class TestUpdateOwnerDTO:
    def test_create_empty_update_owner_dto(self):
        dto = UpdateOwnerDTO()
        assert dto.name is None
        assert dto.email is None
        assert dto.password is None
        assert dto.phone is None

    def test_partial_update_owner_dto(self):
        dto = UpdateOwnerDTO(name='New', phone='11900000000')
        assert dto.name == 'New'
        assert dto.phone == '11900000000'
        assert dto.email is None

    def test_update_owner_dto_exclude_none(self):
        dto = UpdateOwnerDTO(name='Only Name')
        dumped = dto.model_dump(exclude_none=True)
        assert dumped == {'name': 'Only Name'}


@pytest.mark.unit
class TestOwnerOutDTO:
    def test_create_owner_out_dto(self):
        owner_id = uuid4()
        now = datetime.now(timezone.utc)
        dto = OwnerOutDTO(
            id=owner_id,
            name='John',
            email='john@example.com',
            phone='11999999999',
            created_at=now,
        )
        assert dto.id == owner_id
        assert dto.created_at == now

    def test_owner_out_dto_from_attributes_config(self):
        assert OwnerOutDTO.model_config.get('from_attributes') is True


@pytest.mark.unit
class TestOwnerBaseDTO:
    def test_owner_base_dto_from_attributes_config(self):
        assert OwnerBaseDTO.model_config.get('from_attributes') is True

    def test_create_owner_base_dto(self):
        owner_id = uuid4()
        dto = OwnerBaseDTO(
            id=owner_id,
            name='John',
            email='john@example.com',
            password='plain',
            phone='11999999999',
        )
        assert dto.id == owner_id
        assert dto.password == 'plain'
