import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import Request
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.interface.api.v1.controller.employee import EmployeeController
from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee_or_user,
)
from src.interface.api.v1.dependencies.common.pagination import get_pagination_params
from src.interface.api.v1.dependencies.employee import get_employee_controller
from src.interface.api.v1.schema.employee import (
    CreateEmployeeSchema,
    UpdateEmployeeSchema,
)
from src.main import app

URL_EMPLOYEES = '/api/v1/employees'
STATUS_CODE_200 = 200
STATUS_CODE_201 = 201
STATUS_CODE_204 = 204


def _install_overrides() -> AsyncMock:
    mock_controller = AsyncMock(spec=EmployeeController)

    def override_employee_controller():
        return mock_controller

    def override_pagination():
        return PaginationParamsDTO()

    app.dependency_overrides[get_employee_controller] = override_employee_controller
    app.dependency_overrides[get_pagination_params] = override_pagination

    async def override_require_current_employee_or_user(request: Request):
        request.state.company_id = uuid.uuid4()
        request.state.employee_id = uuid.uuid4()
        return request.state.employee_id

    app.dependency_overrides[require_current_employee_or_user] = (
        override_require_current_employee_or_user
    )
    return mock_controller


@pytest.fixture
def override_dependency_employees():
    mock_controller = _install_overrides()
    yield mock_controller
    app.dependency_overrides.clear()


@pytest.mark.unit
class TestEmployeeRoutes:
    def test_list_employees_returns_200(self, client, override_dependency_employees):
        override_dependency_employees.list_employees.return_value = []

        response = client.get(URL_EMPLOYEES)

        assert response.status_code == STATUS_CODE_200, response.json()
        assert response.json() == []

    def test_list_employees_with_pagination(
        self, client, override_dependency_employees, employee_schema
    ):
        override_dependency_employees.list_employees.return_value = [employee_schema]

        response = client.get(f'{URL_EMPLOYEES}?filter_by=name&filter_value=John')

        assert response.status_code == STATUS_CODE_200, response.json()
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == 'John'
        assert data[0]['last_name'] == 'Doe'

    def test_create_employee_returns_201(
        self, client, override_dependency_employees, employee_out_schema
    ):
        override_dependency_employees.create_employee.return_value = employee_out_schema

        payload = CreateEmployeeSchema(
            name='John',
            last_name='Doe',
            phone='11999999999',
            password='plain',
            is_active=True,
            role='admin',
        ).model_dump(mode='json')

        response = client.post(URL_EMPLOYEES, json=payload)

        assert response.status_code == STATUS_CODE_201, response.json()
        data = response.json()
        assert data['name'] == 'John'
        assert data['last_name'] == 'Doe'

    def test_get_employee_returns_200(
        self, client, override_dependency_employees, employee_out_schema
    ):
        employee_id = uuid.uuid4()
        override_dependency_employees.get_employee.return_value = employee_out_schema

        response = client.get(f'{URL_EMPLOYEES}/{employee_id}')

        assert response.status_code == STATUS_CODE_200, response.json()
        assert response.json()['id'] == str(employee_out_schema.id)

    def test_update_employee_returns_200(
        self, client, override_dependency_employees, employee_out_schema
    ):
        employee_id = uuid.uuid4()
        override_dependency_employees.update_employee.return_value = employee_out_schema

        payload = UpdateEmployeeSchema(name='Updated').model_dump(
            mode='json', exclude_none=True
        )
        response = client.patch(f'{URL_EMPLOYEES}/{employee_id}', json=payload)

        assert response.status_code == STATUS_CODE_200, response.json()
        assert response.json()['id'] == str(employee_out_schema.id)

    def test_delete_employee_returns_204(self, client, override_dependency_employees):
        override_dependency_employees.delete_employee.return_value = True

        response = client.delete(f'{URL_EMPLOYEES}/{uuid.uuid4()}')

        assert response.status_code == STATUS_CODE_204, response.json()
