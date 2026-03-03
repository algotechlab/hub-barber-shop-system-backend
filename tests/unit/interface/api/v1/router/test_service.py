import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import Request
from src.interface.api.v1.controller.service import ServiceController
from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee_or_user,
)
from src.interface.api.v1.dependencies.service import get_service_controller
from src.interface.api.v1.schema.service import (
    CreateServiceSchema,
    ServiceSchema,
    UpdateServiceSchema,
    UploadServiceImageOutSchema,
)
from src.main import app

URL_SERVICES = '/api/v1/services'
STATUS_CODE_200 = 200
STATUS_CODE_201 = 201
STATUS_CODE_204 = 204


def _install_overrides() -> AsyncMock:
    mock_controller = AsyncMock(spec=ServiceController)

    def override_service_controller():
        return mock_controller

    app.dependency_overrides[get_service_controller] = override_service_controller

    async def override_require_current_employee_or_user(request: Request):
        request.state.company_id = uuid.uuid4()
        request.state.employee_id = uuid.uuid4()
        return request.state.employee_id

    app.dependency_overrides[require_current_employee_or_user] = (
        override_require_current_employee_or_user
    )
    return mock_controller


@pytest.fixture
def override_dependency_services():
    mock_controller = _install_overrides()
    yield mock_controller
    app.dependency_overrides.clear()


@pytest.mark.unit
class TestServiceRoutes:
    def test_list_services_returns_200(self, client, override_dependency_services):
        service = ServiceSchema(
            id=uuid.uuid4(),
            name='Corte',
            description='Desc',
            price=10.0,
            duration=30,
            category='Cat',
            time_to_spend=30,
            status=True,
            url_image='https://cdn.example.com/a.png',
        )
        override_dependency_services.list_services.return_value = [service]

        response = client.get(URL_SERVICES)

        assert response.status_code == STATUS_CODE_200, response.json()
        assert len(response.json()) == 1

    def test_create_service_returns_201(self, client, override_dependency_services):
        service = ServiceSchema(
            id=uuid.uuid4(),
            name='Corte',
            description='Desc',
            price=10.0,
            duration=30,
            category='Cat',
            time_to_spend=30,
            status=True,
            url_image='https://cdn.example.com/a.png',
        )
        override_dependency_services.create_service.return_value = service

        payload = CreateServiceSchema(
            name='Corte',
            description='Desc',
            price=10.0,
            duration=30,
            category='Cat',
            time_to_spend=30,
            status=True,
            url_image='https://cdn.example.com/a.png',
        ).model_dump(mode='json')

        response = client.post(URL_SERVICES, json=payload)

        assert response.status_code == STATUS_CODE_201, response.json()
        assert response.json()['name'] == 'Corte'

    def test_get_service_returns_200(self, client, override_dependency_services):
        service = ServiceSchema(
            id=uuid.uuid4(),
            name='Corte',
            description='Desc',
            price=10.0,
            duration=30,
            category='Cat',
            time_to_spend=30,
            status=True,
            url_image='https://cdn.example.com/a.png',
        )
        override_dependency_services.get_service.return_value = service

        response = client.get(f'{URL_SERVICES}/{uuid.uuid4()}')

        assert response.status_code == STATUS_CODE_200, response.json()
        assert response.json()['id'] == str(service.id)

    def test_update_service_returns_200(self, client, override_dependency_services):
        service = ServiceSchema(
            id=uuid.uuid4(),
            name='Corte Novo',
            description='Desc',
            price=10.0,
            duration=30,
            category='Cat',
            time_to_spend=30,
            status=True,
            url_image='https://cdn.example.com/a.png',
        )
        override_dependency_services.update_service.return_value = service

        payload = UpdateServiceSchema(name='Corte Novo').model_dump(
            mode='json', exclude_none=True
        )
        response = client.patch(f'{URL_SERVICES}/{uuid.uuid4()}', json=payload)

        assert response.status_code == STATUS_CODE_200, response.json()
        assert response.json()['name'] == 'Corte Novo'

    def test_delete_service_returns_204(self, client, override_dependency_services):
        override_dependency_services.delete_service.return_value = True

        response = client.delete(f'{URL_SERVICES}/{uuid.uuid4()}')

        assert response.status_code == STATUS_CODE_204, response.json()

    def test_upload_service_image_returns_201(
        self, client, override_dependency_services
    ):
        override_dependency_services.upload_service_image.return_value = (
            UploadServiceImageOutSchema(url='https://cdn.example.com/a.png')
        )

        response = client.post(
            f'{URL_SERVICES}/upload-image',
            files={'file': ('a.png', b'fake', 'image/png')},
        )

        assert response.status_code == STATUS_CODE_201, response.json()
        assert response.json()['url'] == 'https://cdn.example.com/a.png'
