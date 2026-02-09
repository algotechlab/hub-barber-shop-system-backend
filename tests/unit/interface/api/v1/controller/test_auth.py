from unittest.mock import AsyncMock

import pytest
from src.domain.dtos.auth import TokenDTO
from src.interface.api.v1.controller.auth import AuthController
from src.interface.api.v1.schema.auth import OwnerLoginSchema

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
