import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from src.domain.dtos.users import UserBaseDTO, UserOutDTO
from src.infrastructure.database.models.users import User
from src.interface.api.v1.schema.users import UserOutSchema
from src.main import app

PLAIN_PASSWORD = 'password'
HASHED_PASSWORD = 'hashed_argon2'


@pytest.fixture
def client():
    with TestClient(app=app, base_url='http://test') as c:
        yield c


@pytest.fixture
def generate_uuid() -> UUID:
    return uuid.uuid4()


@pytest.fixture
def mock_repository_user():
    repo = AsyncMock()
    return repo


@pytest.fixture
def generate_model_user(generate_uuid: UUID) -> User:
    return User(
        id=generate_uuid,
        name='John Doe',
        email='john.doe@example.com',
        password='password',
        is_active=True,
        company_id=uuid.uuid4(),
    )


@pytest.fixture
def generate_user_base_dto(generate_uuid: UUID) -> UserBaseDTO:
    return UserBaseDTO(
        name='John Doe',
        email='john.doe@example.com',
        password=PLAIN_PASSWORD,
        company_id=generate_uuid,
    )


@pytest.fixture
def generate_user_out_dto(generate_uuid: UUID) -> UserOutDTO:
    now = datetime.now(timezone.utc)
    return UserOutDTO(
        id=generate_uuid,
        name='John Doe',
        email='john.doe@example.com',
        password=HASHED_PASSWORD,
        company_id=uuid.uuid4(),
        is_active=True,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def generate_user_out_schema(generate_user_out_dto: UserOutDTO) -> UserOutSchema:
    return UserOutSchema(**{
        k: getattr(generate_user_out_dto, k) for k in UserOutSchema.model_fields
    })
