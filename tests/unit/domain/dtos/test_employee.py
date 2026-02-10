from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.domain.dtos.employee import EmployeeBaseDTO, EmployeeOutDTO, UpdateEmployeeDTO


@pytest.mark.unit
class TestEmployeeBaseDTO:
    def test_create_valid_employee_base_dto(self):
        company_id = uuid4()
        dto = EmployeeBaseDTO(
            name='John',
            last_name='Doe',
            phone='11999999999',
            password='plain',
            is_active=True,
            role='admin',
            company_id=company_id,
        )
        assert dto.name == 'John'
        assert dto.last_name == 'Doe'
        assert dto.phone == '11999999999'
        assert dto.password == 'plain'
        assert dto.is_active is True
        assert dto.role == 'admin'
        assert dto.company_id == company_id

    def test_employee_base_dto_model_dump(self):
        company_id = uuid4()
        dto = EmployeeBaseDTO(
            name='Maria',
            last_name='Silva',
            phone='11988887777',
            password='secret',
            is_active=False,
            role='employee',
            company_id=company_id,
        )
        data = dto.model_dump()
        assert data['name'] == 'Maria'
        assert data['last_name'] == 'Silva'
        assert data['phone'] == '11988887777'
        assert data['password'] == 'secret'
        assert data['is_active'] is False
        assert data['role'] == 'employee'
        assert data['company_id'] == company_id

    def test_employee_base_dto_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            EmployeeBaseDTO(
                name='John',
                # last_name missing
                phone='11999999999',
                is_active=True,
                role='admin',
                company_id=uuid4(),
            )


@pytest.mark.unit
class TestUpdateEmployeeDTO:
    def test_create_empty_update_employee_dto(self):
        dto = UpdateEmployeeDTO()
        assert dto.name is None
        assert dto.last_name is None
        assert dto.phone is None
        assert dto.password is None
        assert dto.is_active is None
        assert dto.role is None
        assert dto.company_id is None

    def test_partial_update_employee_dto(self):
        dto = UpdateEmployeeDTO(name='New', is_active=False)
        assert dto.name == 'New'
        assert dto.is_active is False
        assert dto.last_name is None

    def test_update_employee_dto_exclude_none(self):
        dto = UpdateEmployeeDTO(name='Only Name')
        dumped = dto.model_dump(exclude_none=True)
        assert dumped == {'name': 'Only Name'}


@pytest.mark.unit
class TestEmployeeOutDTO:
    def test_create_employee_out_dto(self):
        employee_id = uuid4()
        company_id = uuid4()
        now = datetime.now(timezone.utc)
        dto = EmployeeOutDTO(
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
        assert dto.id == employee_id
        assert dto.company_id == company_id
        assert dto.created_at == now
        assert dto.updated_at == now

    def test_employee_out_dto_from_attributes_config(self):
        assert EmployeeOutDTO.model_config.get('from_attributes') is True
