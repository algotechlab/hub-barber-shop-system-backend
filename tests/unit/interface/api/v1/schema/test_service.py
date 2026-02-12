from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.interface.api.v1.schema.service import (
    CreateServiceSchema,
    ServiceSchema,
    UpdateServiceSchema,
    UploadServiceImageOutSchema,
)

TIME_TO_SPEND_30 = 30


@pytest.mark.unit
class TestServiceSchema:
    def test_valid_service_schema(self):
        schema = ServiceSchema(
            id=uuid4(),
            name='Corte',
            description='Desc',
            price=10.0,
            duration=30,
            category='Cat',
            time_to_spend=TIME_TO_SPEND_30,
            status=True,
            url_image='https://cdn.example.com/a.png',
        )
        assert schema.name == 'Corte'
        assert schema.time_to_spend == TIME_TO_SPEND_30

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            ServiceSchema(
                id=uuid4(),
                name='Corte',
                description='Desc',
                price=10.0,
                duration=30,
                category='Cat',
                time_to_spend=TIME_TO_SPEND_30,
                status=True,
                # url_image missing
            )


@pytest.mark.unit
class TestCreateServiceSchema:
    def test_valid_create_service_schema(self):
        schema = CreateServiceSchema(
            name='Corte',
            description='Desc',
            price=10.0,
            duration=30,
            category='Cat',
            time_to_spend=TIME_TO_SPEND_30,
            status=True,
            url_image='https://cdn.example.com/a.png',
        )
        assert schema.name == 'Corte'

    def test_model_dump_for_dto(self):
        schema = CreateServiceSchema(
            name='Corte',
            description='Desc',
            price=10.0,
            duration=30,
            category='Cat',
            time_to_spend=TIME_TO_SPEND_30,
            status=True,
            url_image='https://cdn.example.com/a.png',
        )
        data = schema.model_dump()
        assert data['time_to_spend'] == TIME_TO_SPEND_30


@pytest.mark.unit
class TestUpdateServiceSchema:
    def test_empty_update_service_schema(self):
        schema = UpdateServiceSchema()
        assert schema.name is None
        assert schema.url_image is None

    def test_update_service_schema_exclude_none(self):
        schema = UpdateServiceSchema(name='Novo')
        dumped = schema.model_dump(exclude_none=True)
        assert dumped == {'name': 'Novo'}


@pytest.mark.unit
class TestUploadServiceImageOutSchema:
    def test_valid_upload_out_schema(self):
        schema = UploadServiceImageOutSchema(url='https://cdn.example.com/a.png')
        assert schema.url.startswith('https://')
