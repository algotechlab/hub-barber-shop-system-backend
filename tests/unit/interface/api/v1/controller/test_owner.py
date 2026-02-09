from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.owner import OwnerOutDTO, UpdateOwnerDTO
from src.interface.api.v1.controller.owner import OwnerController
from src.interface.api.v1.schema.owner import (
    CreateOwnerSchema,
    OwnerOutSchema,
    UpdateOwnerSchema,
)


@pytest.mark.unit
class TestOwnerController:
    @pytest.fixture
    def mock_use_case(self):
        return AsyncMock()

    @pytest.fixture
    def controller(self, mock_use_case):
        return OwnerController(owner_use_case=mock_use_case)

    async def test_list_owners_returns_schema_list(
        self, controller, mock_use_case, owner_out_dto
    ):
        mock_use_case.list_owners.return_value = [owner_out_dto]
        pagination = PaginationParamsDTO()

        result = await controller.list_owners(pagination)

        mock_use_case.list_owners.assert_awaited_once_with(pagination)
        assert len(result) == 1
        assert isinstance(result[0], OwnerOutSchema)
        assert result[0].email == owner_out_dto.email

    async def test_get_owner_returns_schema_when_found(
        self, controller, mock_use_case, owner_out_dto
    ):
        mock_use_case.get_owner.return_value = owner_out_dto

        result = await controller.get_owner(owner_out_dto.id)

        mock_use_case.get_owner.assert_awaited_once_with(owner_out_dto.id)
        assert result is not None
        assert result.email == owner_out_dto.email

    async def test_get_owner_returns_none_when_use_case_returns_none(
        self, controller, mock_use_case
    ):
        mock_use_case.get_owner.return_value = None

        result = await controller.get_owner(uuid4())

        assert result is None

    async def test_create_owner_returns_schema(self, controller, mock_use_case):
        create_schema = CreateOwnerSchema(
            name='New',
            email='new@example.com',
            password='plain',
            phone='11999999999',
        )
        out_dto = OwnerOutDTO(
            id=uuid4(),
            name=create_schema.name,
            email=create_schema.email,
            phone=create_schema.phone,
            created_at=datetime.now(timezone.utc),
        )
        mock_use_case.create_owner.return_value = out_dto

        result = await controller.create_owner(create_schema)

        assert result.name == create_schema.name
        assert result.email == create_schema.email
        mock_use_case.create_owner.assert_awaited_once()

    async def test_update_owner_returns_schema_when_found(
        self, controller, mock_use_case, owner_out_dto
    ):
        owner_id = owner_out_dto.id
        update_schema = UpdateOwnerSchema(name='Updated', password='plain')
        mock_use_case.update_owner.return_value = owner_out_dto

        result = await controller.update_owner(owner_id, update_schema)

        assert result is not None
        assert result.id == owner_out_dto.id
        mock_use_case.update_owner.assert_awaited_once()
        call_args = mock_use_case.update_owner.call_args[0]
        assert call_args[0] == owner_id
        assert isinstance(call_args[1], UpdateOwnerDTO)
        assert call_args[1].name == 'Updated'
        assert call_args[1].password == 'plain'

    async def test_update_owner_returns_none_when_not_found(
        self, controller, mock_use_case
    ):
        mock_use_case.update_owner.return_value = None

        result = await controller.update_owner(uuid4(), UpdateOwnerSchema(name='X'))

        assert result is None

    async def test_delete_owner_returns_result(self, controller, mock_use_case):
        owner_id = uuid4()
        mock_use_case.delete_owner.return_value = True

        result = await controller.delete_owner(owner_id)

        mock_use_case.delete_owner.assert_awaited_once_with(owner_id)
        assert result is True
