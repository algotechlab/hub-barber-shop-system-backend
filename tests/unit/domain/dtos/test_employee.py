from datetime import datetime, time, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.domain.dtos.employee import (
    EmployeeBaseDTO,
    EmployeeOutDTO,
    UpdateEmployeeDTO,
    _clock_in_journey_bounds,
    validate_employee_journey_pair,
    validate_employee_journey_partial,
)

_JOURNEY_START = time(9, 0)
_JOURNEY_END = time(18, 0)
_BOUNDARY_START = time(8, 30)
_BOUNDARY_END = time(21, 0)


@pytest.mark.unit
class TestClockInJourneyBounds:
    def test_accepts_min_and_max_boundary_times(self):
        _clock_in_journey_bounds(_BOUNDARY_START, 'início')
        _clock_in_journey_bounds(_BOUNDARY_END, 'fim')

    def test_rejects_time_before_journey_min(self):
        with pytest.raises(ValueError, match='entre 08:30 e 21:00'):
            _clock_in_journey_bounds(time(8, 29), 'teste')

    def test_rejects_time_after_journey_max(self):
        with pytest.raises(ValueError, match='entre 08:30 e 21:00'):
            _clock_in_journey_bounds(time(21, 1), 'teste')


@pytest.mark.unit
class TestValidateEmployeeJourneyPair:
    def test_accepts_valid_pair(self):
        validate_employee_journey_pair(_BOUNDARY_START, _BOUNDARY_END)

    def test_raises_when_start_after_end(self):
        with pytest.raises(ValueError, match='anterior ao horário de fim'):
            validate_employee_journey_pair(_JOURNEY_END, _JOURNEY_START)

    def test_raises_when_end_out_of_bounds_before_order_check(self):
        with pytest.raises(ValueError, match='fim'):
            validate_employee_journey_pair(_JOURNEY_START, time(22, 0))


@pytest.mark.unit
class TestValidateEmployeeJourneyPartial:
    def test_no_times_is_noop(self):
        validate_employee_journey_partial(None, None)

    def test_only_start_valid(self):
        validate_employee_journey_partial(_JOURNEY_START, None)

    def test_only_end_valid(self):
        validate_employee_journey_partial(None, _JOURNEY_END)

    def test_only_start_invalid(self):
        with pytest.raises(ValueError, match='início'):
            validate_employee_journey_partial(time(8, 0), None)

    def test_only_end_invalid(self):
        with pytest.raises(ValueError, match='fim'):
            validate_employee_journey_partial(None, time(21, 15))

    def test_both_valid_order(self):
        validate_employee_journey_partial(_JOURNEY_START, _JOURNEY_END)

    def test_both_invalid_order(self):
        with pytest.raises(ValueError, match='anterior ao horário de fim'):
            validate_employee_journey_partial(_JOURNEY_END, _JOURNEY_START)


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
            start_time=_JOURNEY_START,
            end_time=_JOURNEY_END,
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
            start_time=_JOURNEY_START,
            end_time=_JOURNEY_END,
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
                start_time=_JOURNEY_START,
                end_time=_JOURNEY_END,
            )

    def test_employee_base_dto_rejects_start_before_journey_window(self):
        with pytest.raises(ValidationError):
            EmployeeBaseDTO(
                name='John',
                last_name='Doe',
                phone='11999999999',
                password='plain',
                is_active=True,
                role='admin',
                company_id=uuid4(),
                start_time=time(8, 0),
                end_time=_JOURNEY_END,
            )

    def test_employee_base_dto_rejects_end_after_journey_window(self):
        with pytest.raises(ValidationError):
            EmployeeBaseDTO(
                name='John',
                last_name='Doe',
                phone='11999999999',
                password='plain',
                is_active=True,
                role='admin',
                company_id=uuid4(),
                start_time=_JOURNEY_START,
                end_time=time(21, 30),
            )

    def test_employee_base_dto_rejects_start_not_before_end(self):
        with pytest.raises(ValidationError):
            EmployeeBaseDTO(
                name='John',
                last_name='Doe',
                phone='11999999999',
                password='plain',
                is_active=True,
                role='admin',
                company_id=uuid4(),
                start_time=_JOURNEY_END,
                end_time=_JOURNEY_START,
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
        assert dto.start_time is None
        assert dto.end_time is None

    def test_partial_update_employee_dto(self):
        dto = UpdateEmployeeDTO(name='New', is_active=False)
        assert dto.name == 'New'
        assert dto.is_active is False
        assert dto.last_name is None

    def test_update_employee_dto_exclude_none(self):
        dto = UpdateEmployeeDTO(name='Only Name')
        dumped = dto.model_dump(exclude_none=True)
        assert dumped == {'name': 'Only Name'}

    def test_rejects_only_invalid_start_time(self):
        with pytest.raises(ValidationError):
            UpdateEmployeeDTO(start_time=time(8, 0))

    def test_rejects_only_invalid_end_time(self):
        with pytest.raises(ValidationError):
            UpdateEmployeeDTO(end_time=time(22, 0))

    def test_accepts_only_start_time_when_valid(self):
        dto = UpdateEmployeeDTO(start_time=_JOURNEY_START)
        assert dto.end_time is None

    def test_accepts_only_end_time_when_valid(self):
        dto = UpdateEmployeeDTO(end_time=_JOURNEY_END)
        assert dto.start_time is None

    def test_rejects_both_times_when_start_not_before_end(self):
        with pytest.raises(ValidationError):
            UpdateEmployeeDTO(
                start_time=_JOURNEY_END,
                end_time=_JOURNEY_START,
            )


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
            start_time=_JOURNEY_START,
            end_time=_JOURNEY_END,
            created_at=now,
            updated_at=now,
        )
        assert dto.id == employee_id
        assert dto.company_id == company_id
        assert dto.created_at == now
        assert dto.updated_at == now

    def test_employee_out_dto_from_attributes_config(self):
        assert EmployeeOutDTO.model_config.get('from_attributes') is True
