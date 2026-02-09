from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.interface.api.v1.controller.owner import OwnerController
from src.interface.api.v1.dependencies.common.pagination import get_pagination_params
from src.interface.api.v1.dependencies.common.session import get_verified_session
from src.interface.api.v1.dependencies.owner import get_owner_controller
from src.interface.api.v1.schema.owner import OwnerOutSchema
from src.main import app

URL_OWNERS = '/api/v1/owners'


@pytest.fixture
def override_dependency_owners():
    mock_controller = AsyncMock(spec=OwnerController)
    mock_session = AsyncMock()

    async def override_get_verified_session():
        yield mock_session

    def override_get_owner_controller():
        return mock_controller

    def override_get_pagination_params():
        return PaginationParamsDTO()

    app.dependency_overrides[get_verified_session] = override_get_verified_session
    app.dependency_overrides[get_owner_controller] = override_get_owner_controller
    app.dependency_overrides[get_pagination_params] = override_get_pagination_params
    yield mock_controller
    app.dependency_overrides.clear()


def _assert_status(response, expected: int, msg_prefix: str = ''):
    if response.status_code != expected:
        body = response.json() if response.content else response.text
        raise AssertionError(
            f'{msg_prefix}Expected status {expected}, '
            f'got {response.status_code}. Body: {body}'
        )


@pytest.mark.unit
class TestOwnerRoutes:
    def test_list_owners_returns_200(self, client, override_dependency_owners):
        override_dependency_owners.list_owners.return_value = []
        response = client.get(URL_OWNERS)
        _assert_status(response, 200)
        assert response.json() == []

    def test_list_owners_with_pagination(self, client, override_dependency_owners):
        now = datetime.now(timezone.utc)
        owner = OwnerOutSchema(
            id=uuid4(),
            name='John',
            email='john@example.com',
            phone='11999999999',
            created_at=now,
        )
        override_dependency_owners.list_owners.return_value = [owner]

        response = client.get(f'{URL_OWNERS}?filter_by=name&filter_value=John')

        _assert_status(response, 200)
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == 'John'
        assert data[0]['email'] == 'john@example.com'

    def test_create_owner_returns_201(self, client, override_dependency_owners):
        now = datetime.now(timezone.utc)
        owner = OwnerOutSchema(
            id=uuid4(),
            name='John',
            email='john@example.com',
            phone='11999999999',
            created_at=now,
        )
        override_dependency_owners.create_owner.return_value = owner
        payload = {
            'name': 'John',
            'email': 'john@example.com',
            'password': 'plain',
            'phone': '11999999999',
        }

        response = client.post(f'{URL_OWNERS}/', json=payload)

        _assert_status(response, 201)
        data = response.json()
        assert data['name'] == payload['name']
        assert data['email'] == payload['email']

    def test_get_owner_returns_200(self, client, override_dependency_owners):
        now = datetime.now(timezone.utc)
        owner_id = uuid4()
        owner = OwnerOutSchema(
            id=owner_id,
            name='John',
            email='john@example.com',
            phone='11999999999',
            created_at=now,
        )
        override_dependency_owners.get_owner.return_value = owner

        response = client.get(f'{URL_OWNERS}/{owner_id}')

        _assert_status(response, 200)
        data = response.json()
        assert data['id'] == str(owner_id)

    def test_update_owner_returns_200(self, client, override_dependency_owners):
        now = datetime.now(timezone.utc)
        owner_id = uuid4()
        owner = OwnerOutSchema(
            id=owner_id,
            name='Updated',
            email='john@example.com',
            phone='11999999999',
            created_at=now,
        )
        override_dependency_owners.update_owner.return_value = owner

        response = client.patch(
            f'{URL_OWNERS}/{owner_id}',
            json={'name': 'Updated'},
        )

        _assert_status(response, 200)
        data = response.json()
        assert data['name'] == 'Updated'

    def test_delete_owner_returns_204(self, client, override_dependency_owners):
        owner_id = uuid4()
        override_dependency_owners.delete_owner.return_value = None

        response = client.delete(f'{URL_OWNERS}/{owner_id}')

        _assert_status(response, 204)
