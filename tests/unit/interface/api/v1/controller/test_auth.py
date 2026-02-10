from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.auth import TokenDTO, TokenWithCompanyDTO
from src.interface.api.v1.controller.auth import AuthController
from src.interface.api.v1.schema.auth import (
    EmployeeLoginSchema,
    OwnerLoginSchema,
    UserLoginSchema,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_login_owner_returns_token_schema():
    use_case = AsyncMock()
    use_case.login_owner.return_value = TokenDTO(access_token='tok')
    controller = AuthController(use_case)

    result = await controller.login_owner(
        OwnerLoginSchema(email='john@example.com', password='plain')
    )

    assert result.access_token == 'tok'
    assert result.token_type == 'bearer'
    use_case.login_owner.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_employee_returns_token_with_company_schema():
    use_case = AsyncMock()
    company_id = uuid4()
    employee_id = uuid4()
    use_case.login_employee.return_value = TokenWithCompanyDTO(
        id=employee_id, name='John', access_token='tok', company_id=company_id
    )
    controller = AuthController(use_case)

    result = await controller.login_employee(
        EmployeeLoginSchema(phone='11999999999', password='plain')
    )

    assert result.access_token == 'tok'
    assert result.company_id == company_id
    assert result.id == employee_id
    assert result.name == 'John'
    use_case.login_employee.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_user_returns_token_with_company_schema():
    use_case = AsyncMock()
    company_id = uuid4()
    user_id = uuid4()
    use_case.login_user.return_value = TokenWithCompanyDTO(
        id=user_id, name='John', access_token='tok', company_id=company_id
    )
    controller = AuthController(use_case)

    result = await controller.login_user(UserLoginSchema(phone='11999999999'))

    assert result.access_token == 'tok'
    assert result.company_id == company_id
    assert result.id == user_id
    assert result.name == 'John'
    use_case.login_user.assert_awaited_once()
