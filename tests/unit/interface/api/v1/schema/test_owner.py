from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.domain.dtos.owner import CreateOwnerDTO, OwnerOutDTO
from src.interface.api.v1.schema.owner import (
    CreateOwnerSchema,
    OwnerOutSchema,
    OwnerSchema,
    UpdateOwnerSchema,
)


@pytest.mark.unit
class TestOwnerSchema:
    def test_valid_owner_schema(self):
        now = datetime.now(timezone.utc)
        schema = OwnerSchema(
            id=uuid4(),
            name='John',
            email='john@example.com',
            password='plain',
            phone='11999999999',
            created_at=now,
        )
        assert schema.name == 'John'
        assert schema.created_at == now

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            OwnerSchema(
                id=uuid4(),
                name='John',
                email='john@example.com',
                # password missing
                phone='11999999999',
                created_at=datetime.now(timezone.utc),
            )


@pytest.mark.unit
class TestCreateOwnerSchema:
    def test_valid_create_owner_schema(self):
        dto = CreateOwnerDTO(
            name='John',
            email='john@example.com',
            password='plain',
            phone='11999999999',
        )
        schema = CreateOwnerSchema(**dto.model_dump())
        assert schema.name == dto.name
        assert schema.email == dto.email

    def test_model_dump_for_dto(self):
        schema = CreateOwnerSchema(
            name='John',
            email='john@example.com',
            password='plain',
            phone='11999999999',
        )
        data = schema.model_dump()
        assert data['email'] == 'john@example.com'


@pytest.mark.unit
class TestUpdateOwnerSchema:
    def test_empty_update_schema(self):
        schema = UpdateOwnerSchema()
        assert schema.name is None
        assert schema.email is None
        assert schema.password is None
        assert schema.phone is None

    def test_partial_update_schema(self):
        schema = UpdateOwnerSchema(name='New')
        dumped = schema.model_dump(exclude_none=True)
        assert dumped == {'name': 'New'}


@pytest.mark.unit
class TestOwnerOutSchema:
    def test_valid_owner_out_schema(self):
        now = datetime.now(timezone.utc)
        dto = OwnerOutDTO(
            id=uuid4(),
            name='John',
            email='john@example.com',
            phone='11999999999',
            created_at=now,
        )
        schema = OwnerOutSchema(**dto.model_dump())
        assert schema.id == dto.id
        assert schema.created_at == now
