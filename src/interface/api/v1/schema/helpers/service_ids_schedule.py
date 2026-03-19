from __future__ import annotations

from typing import Optional
from uuid import UUID


def _service_id_item_to_uuid(item: object) -> UUID:
    if isinstance(item, dict):
        raise ValueError(
            'service_id deve ser uma lista de UUIDs, ex.: '
            '["uuid-servico-1", "uuid-servico-2"]. Não use {"id": "..."} por item.'
        )
    if isinstance(item, UUID):
        return item
    if isinstance(item, str):
        return UUID(item)
    raise TypeError(
        'Cada item de service_id deve ser string (UUID) ou UUID; '
        f'recebido {type(item).__name__}.'
    )


def coerce_service_ids(value: object) -> list[UUID]:
    if value is None:
        raise ValueError('service_id é obrigatório')
    if isinstance(value, UUID):
        return [value]
    if isinstance(value, str):
        return [UUID(value)]
    if not isinstance(value, list):
        raise TypeError('service_id deve ser uma lista de UUIDs')
    return [_service_id_item_to_uuid(item) for item in value]


def coerce_optional_service_ids(value: object) -> Optional[list[UUID]]:
    if value is None:
        return None
    return coerce_service_ids(value)
