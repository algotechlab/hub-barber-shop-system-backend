from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.domain.dtos.service import (
    CreateServiceDTO,
    ServiceDTO,
    ServiceOutDTO,
    UpdateServiceDTO,
)

TIME_TO_SPEND_30 = 30
TIME_TO_SPEND_45 = 45
TIME_TO_SPEND_90 = 90


@pytest.mark.unit
class TestCreateServiceDTO:
    def test_create_valid_create_service_dto(self):
        company_id = uuid4()
        dto = CreateServiceDTO(
            name='Corte',
            description='Corte masculino',
            price=Decimal('10'),
            duration=30,
            category='Cabelo',
            time_to_spend=TIME_TO_SPEND_30,
            status=True,
            url_image='https://cdn.example.com/a.png',
            company_id=company_id,
        )
        assert dto.company_id == company_id
        assert dto.time_to_spend == TIME_TO_SPEND_30

    def test_create_service_dto_model_dump(self):
        dto = CreateServiceDTO(
            name='Corte',
            description='Corte masculino',
            price=Decimal('10'),
            duration=30,
            category='Cabelo',
            time_to_spend=TIME_TO_SPEND_45,
            status=True,
            url_image='https://cdn.example.com/a.png',
            company_id=uuid4(),
        )
        data = dto.model_dump()
        assert data['name'] == 'Corte'
        assert data['time_to_spend'] == TIME_TO_SPEND_45

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            CreateServiceDTO(
                name='Corte',
                description='Corte masculino',
                price=Decimal('10'),
                duration=30,
                category='Cabelo',
                time_to_spend=TIME_TO_SPEND_30,
                status=True,
                # url_image missing
                company_id=uuid4(),
            )


@pytest.mark.unit
class TestUpdateServiceDTO:
    def test_create_empty_update_service_dto(self):
        dto = UpdateServiceDTO()
        assert dto.name is None
        assert dto.time_to_spend is None

    def test_update_service_dto_exclude_none(self):
        dto = UpdateServiceDTO(name='Novo', time_to_spend=60)
        dumped = dto.model_dump(exclude_none=True)
        assert dumped == {'name': 'Novo', 'time_to_spend': 60}


@pytest.mark.unit
class TestServiceDTO:
    def test_service_dto_from_attributes_config(self):
        assert ServiceDTO.model_config.get('from_attributes') is True

    def test_time_to_spend_normalizes_from_timedelta(self):
        company_id = uuid4()
        obj = SimpleNamespace(
            id=uuid4(),
            name='Corte',
            description='Desc',
            price=Decimal('10'),
            duration=30,
            category='Cabelo',
            time_to_spend=timedelta(minutes=TIME_TO_SPEND_90),
            status=True,
            url_image='https://cdn.example.com/a.png',
            company_id=company_id,
        )

        dto = ServiceDTO.model_validate(obj)

        assert dto.company_id == company_id
        assert dto.time_to_spend == TIME_TO_SPEND_90

    def test_service_out_dto_from_attributes_config(self):
        assert ServiceOutDTO.model_config.get('from_attributes') is True

    def test_service_out_dto_time_to_spend_normalizes_from_timedelta(self):
        now = datetime.now(timezone.utc)
        obj = SimpleNamespace(
            id=uuid4(),
            name='Corte',
            description='Desc',
            price=Decimal('10'),
            duration=30,
            category='Cabelo',
            time_to_spend=timedelta(minutes=TIME_TO_SPEND_30),
            status=True,
            url_image='https://cdn.example.com/a.png',
            created_at=now,
        )

        dto = ServiceOutDTO.model_validate(obj)

        assert dto.created_at == now
        assert dto.time_to_spend == TIME_TO_SPEND_30

    def test_service_out_dto_time_to_spend_keeps_int_value(self):
        now = datetime.now(timezone.utc)
        obj = SimpleNamespace(
            id=uuid4(),
            name='Corte',
            description='Desc',
            price=Decimal('10'),
            duration=30,
            category='Cabelo',
            time_to_spend=TIME_TO_SPEND_30,
            status=True,
            url_image='https://cdn.example.com/a.png',
            created_at=now,
        )

        dto = ServiceOutDTO.model_validate(obj)

        assert dto.time_to_spend == TIME_TO_SPEND_30
