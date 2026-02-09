from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.employee import UpdateEmployeeDTO
from src.domain.use_case.employee import EmployeeUseCase


@pytest.mark.unit
class TestEmployeeUseCase:
    @pytest.fixture
    def mock_service(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_service):
        return EmployeeUseCase(employee_service=mock_service)

    async def test_list_employees_delegates_to_service(
        self, use_case, mock_service, employee_out_dto
    ):
        pagination = PaginationParamsDTO()
        mock_service.list_employees.return_value = [employee_out_dto]

        result = await use_case.list_employees(pagination)

        mock_service.list_employees.assert_awaited_once_with(pagination)
        assert result == [employee_out_dto]

    @patch('src.domain.use_case.employee.hash_password')
    async def test_create_employee_hashes_password_before_create(
        self,
        mock_hash_password,
        use_case,
        mock_service,
        employee_base_dto,
        employee_out_dto,
    ):
        mock_hash_password.return_value = 'hashed_argon2'
        mock_service.create_employee.return_value = employee_out_dto

        result = await use_case.create_employee(employee_base_dto)

        mock_hash_password.assert_called_once_with('plain')
        call_employee = mock_service.create_employee.call_args[0][0]
        assert call_employee.password == 'hashed_argon2'
        assert result == employee_out_dto

    async def test_get_employee_delegates_to_service(
        self, use_case, mock_service, employee_out_dto
    ):
        employee_id = uuid4()
        mock_service.get_employee.return_value = employee_out_dto

        result = await use_case.get_employee(employee_id)

        mock_service.get_employee.assert_awaited_once_with(employee_id)
        assert result == employee_out_dto

    async def test_update_employee_delegates_to_service(
        self, use_case, mock_service, employee_out_dto
    ):
        employee_id = uuid4()
        update_dto = UpdateEmployeeDTO(name='Updated')
        mock_service.update_employee.return_value = employee_out_dto

        result = await use_case.update_employee(employee_id, update_dto)

        mock_service.update_employee.assert_awaited_once_with(employee_id, update_dto)
        assert result == employee_out_dto

    async def test_delete_employee_delegates_to_service(self, use_case, mock_service):
        employee_id = uuid4()
        mock_service.delete_employee.return_value = True

        result = await use_case.delete_employee(employee_id)

        mock_service.delete_employee.assert_awaited_once_with(employee_id)
        assert result is True
