from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class PaginationParamsBaseSchema(BaseModel):
    page: Optional[int] = Field(
        default=None,
        ge=1,
    )

    offset: int = Field(
        default=0,
        ge=0,
        description=(
            'Compat: se offset>=1, ele será tratado como número da página (1-index) '
            'e convertido para offset real. Se offset=0, equivale à primeira página.'
        ),
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description='Limite de registros por página',
    )

    filter_by: Optional[str] = Field(
        default=None, description='Campo utilizado para filtrar resultados'
    )

    filter_value: Optional[str] = Field(
        default=None, description='O valor a ser buscado'
    )

    @field_validator('filter_by')
    @classmethod
    def validate_filter_fields(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed_fields = [
            'username',
            'name',
            'document',
            'description',
            'category',
            'phone',
            'email',
            'slug',
            'last_name',
            'role',
        ]
        if value not in allowed_fields:
            raise ValueError(
                f'O campo filter_by deve ser um dos  '
                f'seguintes: {", ".join(allowed_fields)}'
            )
        return value

    @model_validator(mode='after')
    def check_filter_pair(self) -> 'PaginationParamsBaseSchema':
        if self.filter_by and not self.filter_value:
            raise ValueError(
                'Se você definiu filter_by, precisa enviar o filter_value.'
            )
        if self.filter_value and not self.filter_by:
            raise ValueError(
                'Se você enviou um valor de busca (filter_value), '
                'precisa definir por onde filtrar (filter_by).'
            )
        return self
