from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.employee import UpdateEmployeeDTO
from src.domain.service.employee import EmployeeService


@pytest.mark.unit
class TestEmployeeService:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository):
        return EmployeeService(employee_repository=mock_repository)

    async def test_list_employees_delegates_to_repository(
        self, service, mock_repository, employee_out_dto
    ):
        pagination = PaginationParamsDTO()
        company_id = uuid4()
        mock_repository.list_employees.return_value = [employee_out_dto]

        result = await service.list_employees(pagination, company_id)

        mock_repository.list_employees.assert_awaited_once_with(pagination, company_id)
        assert result == [employee_out_dto]

    async def test_create_employee_delegates_to_repository(
        self, service, mock_repository, employee_base_dto, employee_out_dto
    ):
        mock_repository.create_employee.return_value = employee_out_dto

        result = await service.create_employee(employee_base_dto)

        mock_repository.create_employee.assert_awaited_once_with(employee_base_dto)
        assert result == employee_out_dto

    async def test_get_employee_delegates_to_repository(
        self, service, mock_repository, employee_out_dto
    ):
        employee_id = uuid4()
        company_id = uuid4()
        mock_repository.get_employee.return_value = employee_out_dto

        result = await service.get_employee(employee_id, company_id)

        mock_repository.get_employee.assert_awaited_once_with(employee_id, company_id)
        assert result == employee_out_dto

    async def test_get_employee_returns_none_when_not_found(
        self, service, mock_repository
    ):
        employee_id = uuid4()
        company_id = uuid4()
        mock_repository.get_employee.return_value = None

        result = await service.get_employee(employee_id, company_id)

        mock_repository.get_employee.assert_awaited_once_with(employee_id, company_id)
        assert result is None

    async def test_get_employee_auth_by_phone_delegates_to_repository(
        self, service, mock_repository
    ):
        mock_repository.get_employee_auth_by_phone.return_value = None

        result = await service.get_employee_auth_by_phone('11999999999')

        mock_repository.get_employee_auth_by_phone.assert_awaited_once_with(
            '11999999999'
        )
        assert result is None

    async def test_update_employee_delegates_to_repository(
        self, service, mock_repository, employee_out_dto
    ):
        employee_id = uuid4()
        company_id = uuid4()
        update_dto = UpdateEmployeeDTO(name='Updated')
        mock_repository.update_employee.return_value = employee_out_dto

        result = await service.update_employee(employee_id, update_dto, company_id)

        mock_repository.update_employee.assert_awaited_once_with(
            employee_id, update_dto, company_id
        )
        assert result == employee_out_dto

    async def test_delete_employee_delegates_to_repository(
        self, service, mock_repository
    ):
        employee_id = uuid4()
        company_id = uuid4()
        mock_repository.delete_employee.return_value = True

        result = await service.delete_employee(employee_id, company_id)

        mock_repository.delete_employee.assert_awaited_once_with(
            employee_id, company_id
        )
        assert result is True
