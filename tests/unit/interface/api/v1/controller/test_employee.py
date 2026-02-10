from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.employee import EmployeeBaseDTO, UpdateEmployeeDTO
from src.interface.api.v1.controller.employee import EmployeeController
from src.interface.api.v1.schema.common.pagination import PaginationParamsBaseSchema
from src.interface.api.v1.schema.employee import (
    CreateEmployeeSchema,
    EmployeeOutSchema,
    EmployeeSchema,
    UpdateEmployeeSchema,
)


@pytest.mark.unit
class TestEmployeeController:
    @pytest.fixture
    def mock_employee_use_case(self):
        return AsyncMock()

    @pytest.fixture
    def employee_controller(self, mock_employee_use_case):
        return EmployeeController(employee_use_case=mock_employee_use_case)

    async def test_list_employees_delegates_to_use_case(
        self, employee_controller, mock_employee_use_case
    ):
        pagination = PaginationParamsBaseSchema()
        company_id = uuid4()
        expected = [
            EmployeeSchema(
                id=uuid4(),
                name='John',
                last_name='Doe',
                phone='11999999999',
                is_active=True,
                role='admin',
                company_id=uuid4(),
            )
        ]
        mock_employee_use_case.list_employees.return_value = expected

        result = await employee_controller.list_employees(pagination, company_id)

        mock_employee_use_case.list_employees.assert_awaited_once_with(
            pagination, company_id
        )
        assert result == expected

    async def test_create_employee_converts_schema_to_dto_and_returns_schema(
        self, employee_controller, mock_employee_use_case, employee_out_dto
    ):
        company_id = uuid4()
        create_schema = CreateEmployeeSchema(
            name='John',
            last_name='Doe',
            phone='11999999999',
            password='plain',
            is_active=True,
            role='admin',
        )
        mock_employee_use_case.create_employee.return_value = employee_out_dto

        result = await employee_controller.create_employee(
            create_schema, company_id=company_id
        )

        mock_employee_use_case.create_employee.assert_awaited_once()
        called_arg = mock_employee_use_case.create_employee.call_args[0][0]
        assert isinstance(called_arg, EmployeeBaseDTO)
        assert called_arg.name == create_schema.name
        assert called_arg.last_name == create_schema.last_name
        assert called_arg.phone == create_schema.phone
        assert called_arg.password == create_schema.password
        assert called_arg.is_active == create_schema.is_active
        assert called_arg.role == create_schema.role
        assert called_arg.company_id == company_id

        assert isinstance(result, EmployeeOutSchema)
        assert result.id == employee_out_dto.id
        assert result.created_at == employee_out_dto.created_at

    async def test_get_employee_returns_schema(
        self, employee_controller, mock_employee_use_case, employee_out_dto
    ):
        employee_id = uuid4()
        company_id = uuid4()
        mock_employee_use_case.get_employee.return_value = employee_out_dto

        result = await employee_controller.get_employee(employee_id, company_id)

        mock_employee_use_case.get_employee.assert_awaited_once_with(
            employee_id, company_id
        )
        assert isinstance(result, EmployeeOutSchema)
        assert result.id == employee_out_dto.id
        assert result.name == employee_out_dto.name

    async def test_update_employee_converts_schema_to_dto_and_returns_schema(
        self, employee_controller, mock_employee_use_case, employee_out_dto
    ):
        employee_id = uuid4()
        company_id = uuid4()
        update_schema = UpdateEmployeeSchema(name='Updated', phone='11888887777')
        mock_employee_use_case.update_employee.return_value = employee_out_dto

        result = await employee_controller.update_employee(
            employee_id, update_schema, company_id
        )

        mock_employee_use_case.update_employee.assert_awaited_once()
        call_args = mock_employee_use_case.update_employee.call_args[0]
        assert call_args[0] == employee_id
        assert isinstance(call_args[1], UpdateEmployeeDTO)
        assert call_args[1].name == 'Updated'
        assert call_args[1].phone == '11888887777'
        assert call_args[2] == company_id

        assert isinstance(result, EmployeeOutSchema)
        assert result.id == employee_out_dto.id

    async def test_delete_employee_delegates_to_use_case(
        self, employee_controller, mock_employee_use_case
    ):
        employee_id = uuid4()
        company_id = uuid4()
        mock_employee_use_case.delete_employee.return_value = True

        result = await employee_controller.delete_employee(employee_id, company_id)

        mock_employee_use_case.delete_employee.assert_awaited_once_with(
            employee_id, company_id
        )
        assert result is True
