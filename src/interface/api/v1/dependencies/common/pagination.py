from typing import Annotated

from fastapi import Depends

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.interface.api.v1.schema.common.pagination import PaginationParamsBaseSchema


def get_pagination_params(
    schema: PaginationParamsBaseSchema = Depends(),
) -> PaginationParamsDTO:
    # Compat: muitos clientes usam "offset" como número da página (1-index).
    # - Se "page" vier, ele sempre ganha.
    # - Senão, se "offset" >= 1, tratamos como página e convertemos para offset real.
    # - "offset=0" continua significando primeira página.
    if schema.page is not None:
        offset = (schema.page - 1) * schema.limit
    else:
        page_from_offset = max(schema.offset, 0)
        if page_from_offset >= 1:
            offset = (page_from_offset - 1) * schema.limit
        else:
            offset = 0

    return PaginationParamsDTO(
        page=schema.page,
        offset=offset,
        limit=schema.limit,
        filter_by=schema.filter_by,
        filter_value=schema.filter_value,
    )


PaginationParamsDep = Annotated[PaginationParamsDTO, Depends(get_pagination_params)]
