from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.interface.api.v1.schema.employee import (
    CreateEmployeeSchema,
    EmployeeOutSchema,
    EmployeeSchema,
    UpdateEmployeeSchema,
)


@pytest.mark.unit
class TestEmployeeSchema:
    def test_valid_employee_schema(self):
        employee_id = uuid4()
        company_id = uuid4()

        schema = EmployeeSchema(
            id=employee_id,
            name='John',
            last_name='Doe',
            phone='11999999999',
            is_active=True,
            role='admin',
            company_id=company_id,
        )

        assert schema.id == employee_id
        assert schema.company_id == company_id
        assert schema.name == 'John'
        assert schema.last_name == 'Doe'
        assert schema.is_active is True

    def test_employee_schema_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            EmployeeSchema(
                id=uuid4(),
                name='John',
                # last_name missing
                phone='11999999999',
                is_active=True,
                role='admin',
                company_id=uuid4(),
            )


@pytest.mark.unit
class TestCreateEmployeeSchema:
    def test_valid_create_employee_schema(self):
        schema = CreateEmployeeSchema(
            name='Maria',
            last_name='Silva',
            phone='11988887777',
            password='plain',
            is_active=True,
            role='employee',
        )

        assert schema.name == 'Maria'
        assert schema.last_name == 'Silva'
        assert schema.phone == '11988887777'
        assert schema.password == 'plain'
        assert schema.role == 'employee'

    def test_create_employee_schema_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            CreateEmployeeSchema(
                name='Maria',
                last_name='Silva',
                phone='11988887777',
                # password missing
                is_active=True,
                role='employee',
            )


@pytest.mark.unit
class TestUpdateEmployeeSchema:
    def test_empty_update_employee_schema(self):
        schema = UpdateEmployeeSchema()
        assert schema.name is None
        assert schema.last_name is None
        assert schema.phone is None
        assert schema.password is None
        assert schema.is_active is None
        assert schema.role is None
        assert schema.company_id is None

    def test_partial_update_employee_schema(self):
        schema = UpdateEmployeeSchema(name='New Name', is_active=False)
        assert schema.name == 'New Name'
        assert schema.is_active is False
        assert schema.last_name is None

    def test_update_employee_schema_exclude_none(self):
        schema = UpdateEmployeeSchema(name='Only Name')
        dumped = schema.model_dump(exclude_none=True)
        assert dumped == {'name': 'Only Name'}


@pytest.mark.unit
class TestEmployeeOutSchema:
    def test_valid_employee_out_schema(self):
        now = datetime.now(timezone.utc)
        employee_id = uuid4()
        company_id = uuid4()

        schema = EmployeeOutSchema(
            id=employee_id,
            name='John',
            last_name='Doe',
            phone='11999999999',
            is_active=True,
            role='admin',
            company_id=company_id,
            created_at=now,
            updated_at=now,
        )

        assert schema.id == employee_id
        assert schema.company_id == company_id
        assert schema.created_at == now
        assert schema.updated_at == now
