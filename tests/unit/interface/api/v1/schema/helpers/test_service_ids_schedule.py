from uuid import UUID

import pytest
from src.interface.api.v1.schema.helpers import service_ids_schedule as m

pytestmark = pytest.mark.unit


def test_coerce_service_ids_rejects_none():
    with pytest.raises(ValueError, match='obrigatório'):
        m.coerce_service_ids(None)


def test_coerce_service_ids_accepts_single_uuid():
    u = UUID('3fa85f64-5717-4562-b3fc-2c963f66afa6')
    assert m.coerce_service_ids(u) == [u]


def test_coerce_service_ids_accepts_single_uuid_string():
    s = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
    assert m.coerce_service_ids(s) == [UUID(s)]


def test_coerce_service_ids_accepts_list_of_strings():
    ids = [
        '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        'baf26222-1b35-452d-842e-668c2c33bd0e',
    ]
    assert m.coerce_service_ids(ids) == [UUID(ids[0]), UUID(ids[1])]


def test_coerce_service_ids_rejects_non_list():
    with pytest.raises(TypeError, match='lista'):
        m.coerce_service_ids({'not': 'a list'})


def test_coerce_service_ids_rejects_dict_item():
    with pytest.raises(ValueError, match='lista de UUIDs'):
        m.coerce_service_ids([{'id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'}])


def test_coerce_service_ids_rejects_non_uuid_item():
    with pytest.raises(TypeError, match='recebido int'):
        m.coerce_service_ids([123])


def test_coerce_optional_service_ids_none():
    assert m.coerce_optional_service_ids(None) is None


def test_coerce_optional_service_ids_delegates_to_coerce():
    s = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
    assert m.coerce_optional_service_ids([s]) == [UUID(s)]


def test_service_id_item_dict_raises():
    with pytest.raises(ValueError, match='lista de UUIDs'):
        m._service_id_item_to_uuid({'id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'})
