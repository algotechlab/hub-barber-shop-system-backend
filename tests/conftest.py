import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from src.domain.dtos.employee import EmployeeBaseDTO, EmployeeOutDTO
from src.domain.dtos.owner import CreateOwnerDTO, OwnerOutDTO
from src.domain.dtos.schedule_block import (
    ScheduleBlockCreateDTO,
    ScheduleBlockOutDTO,
    ScheduleBlockOutListDTO,
)
from src.domain.dtos.users import UserBaseDTO, UserOutDTO
from src.infrastructure.database.models.employees import Employee
from src.infrastructure.database.models.users import User
from src.interface.api.v1.schema.employee import EmployeeOutSchema, EmployeeSchema
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
        phone='11999999999',
        password='password',
        is_active=True,
        company_id=uuid.uuid4(),
    )


@pytest.fixture
def employee_schema() -> EmployeeSchema:
    return EmployeeSchema(
        id=uuid.uuid4(),
        name='John',
        last_name='Doe',
        phone='11999999999',
        is_active=True,
        role='admin',
        company_id=uuid.uuid4(),
    )


@pytest.fixture
def employee_out_schema() -> EmployeeOutSchema:
    now = datetime.now(timezone.utc)
    return EmployeeOutSchema(
        id=uuid.uuid4(),
        name='John',
        last_name='Doe',
        phone='11999999999',
        is_active=True,
        role='admin',
        company_id=uuid.uuid4(),
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def employee_base_dto():
    return EmployeeBaseDTO(
        name='John',
        last_name='Doe',
        phone='11999999999',
        password='plain',
        is_active=True,
        role='admin',
        company_id=uuid.uuid4(),
    )


@pytest.fixture
def generate_model_employee(generate_uuid: UUID) -> Employee:
    return Employee(
        id=generate_uuid,
        name='John Doe',
        last_name='Doe',
        phone='1234567890',
        password='password',
        is_active=True,
    )


@pytest.fixture
def employee_out_dto(employee_base_dto):
    now = datetime.now(timezone.utc)
    return EmployeeOutDTO(
        id=uuid.uuid4(),
        name=employee_base_dto.name,
        last_name=employee_base_dto.last_name,
        phone=employee_base_dto.phone,
        is_active=employee_base_dto.is_active,
        role=employee_base_dto.role,
        company_id=employee_base_dto.company_id,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def generate_user_base_dto(generate_uuid: UUID) -> UserBaseDTO:
    return UserBaseDTO(
        name='John Doe',
        email='john.doe@example.com',
        password=PLAIN_PASSWORD,
        phone='11999999999',
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
        phone='11999999999',
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


@pytest.fixture
def owner_create_dto():
    return CreateOwnerDTO(
        name='John',
        email='john@example.com',
        password='plain',
        phone='11999999999',
    )


@pytest.fixture
def owner_out_dto(owner_create_dto):
    return OwnerOutDTO(
        id=uuid4(),
        name=owner_create_dto.name,
        email=owner_create_dto.email,
        phone=owner_create_dto.phone,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def generate_schedule_block_create_dto():
    return ScheduleBlockCreateDTO(
        employee_id=uuid4(),
        company_id=uuid4(),
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
    )


@pytest.fixture
def generate_schedule_block_out_dto():
    return ScheduleBlockOutDTO(
        id=uuid4(),
        employee_id=uuid4(),
        company_id=uuid4(),
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        is_block=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def generate_schedule_block_out_list_dto():
    """Fixture para gerar um ScheduleBlockOutListDTO"""
    return [
        ScheduleBlockOutListDTO(
            id=uuid4(),
            employee_id=uuid4(),
            employee_name='John Doe',
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            is_block=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    ]
