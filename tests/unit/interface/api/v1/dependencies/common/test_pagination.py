import pytest
from pydantic import ValidationError
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.interface.api.v1.dependencies.common.pagination import get_pagination_params
from src.interface.api.v1.schema.common.pagination import PaginationParamsBaseSchema


@pytest.mark.parametrize(
    ('filter_by', 'filter_value', 'should_pass'),
    [
        # Casos válidos
        (None, None, True),  # Sem filtro
        ('username', 'john', True),  # Filtro válido
        ('name', 'John Doe', True),  # Filtro com valor numérico como str
        ('description', 'John Doe', True),  # Filtro com valor numérico como str
        ('email', 'john@example.com', True),  # Campo agora permitido
    ],
)
def test_pagination_params_valid(filter_by, filter_value, should_pass):
    # Act & Assert
    if should_pass:
        params = PaginationParamsBaseSchema(
            filter_by=filter_by, filter_value=filter_value
        )
        assert params.filter_by == filter_by
        assert params.filter_value == filter_value
    else:
        with pytest.raises(ValidationError):
            PaginationParamsBaseSchema(filter_by=filter_by, filter_value=filter_value)


@pytest.mark.parametrize(
    ('filter_by', 'filter_value', 'expected_msg'),
    [
        # filter_by inválido (nota o espaço extra no schema: "dos  seguintes")
        ('invalid', None, 'O campo filter_by deve ser um dos  seguintes:'),
        # Par inválido: filter_by sem filter_value
        ('username', None, 'Se você definiu filter_by, precisa enviar o filter_value.'),
        # Par inválido: filter_value sem filter_by
        (
            None,
            'john',
            (
                'Se você enviou um valor de busca (filter_value), '
                'precisa definir por onde filtrar (filter_by).'
            ),
        ),
    ],
)
def test_pagination_params_invalid(filter_by, filter_value, expected_msg):
    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        PaginationParamsBaseSchema(filter_by=filter_by, filter_value=filter_value)

    errors = exc_info.value.errors()
    assert any(expected_msg in error['msg'] for error in errors)


@pytest.mark.unit
@pytest.mark.parametrize(
    ('filter_by', 'filter_value'),
    [
        (None, None),
        ('username', 'john'),
        ('name', 'John Doe'),
        ('description', 'barber'),
    ],
)
def test_get_pagination_params_returns_dto(filter_by, filter_value):
    schema = PaginationParamsBaseSchema(filter_by=filter_by, filter_value=filter_value)

    dto = get_pagination_params(schema=schema)

    assert isinstance(dto, PaginationParamsDTO)
    assert dto.filter_by == filter_by
    assert dto.filter_value == filter_value


def test_get_pagination_params_converts_offset_as_page_when_no_page_is_sent():
    schema = PaginationParamsBaseSchema(offset=2, limit=10)
    dto = get_pagination_params(schema=schema)
    offeset = 10
    assert dto.offset == offeset


def test_get_pagination_params_page_has_priority_over_offset():
    schema = PaginationParamsBaseSchema(page=2, offset=1, limit=10)
    dto = get_pagination_params(schema=schema)
    offeset = 10
    assert dto.offset == offeset
