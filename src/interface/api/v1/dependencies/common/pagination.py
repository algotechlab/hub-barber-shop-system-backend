from typing import Annotated

from fastapi import Depends

from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.interface.api.v1.schema.common.pagination import PaginationParamsBaseSchema


def get_pagination_params(
    schema: PaginationParamsBaseSchema = Depends(),
) -> PaginationParamsDTO:
    return PaginationParamsDTO(
        filter_by=schema.filter_by,
        filter_value=schema.filter_value,
    )


PaginationParamsDep = Annotated[
    PaginationParamsBaseSchema, Depends(get_pagination_params)
]
