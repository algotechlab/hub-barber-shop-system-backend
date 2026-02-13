import pytest
from pydantic import ValidationError
from src.domain.dtos.common.pagination import PaginationParamsDTO

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ('filter_by', 'filter_value', 'should_pass'),
    [
        # Casos válidos
        (None, None, True),  # Sem filtro
        ('username', 'john', True),  # Filtro válido
        ('username', '123', True),  # Filtro com valor numérico como str
        ('email', 'john', True),  # Campo agora permitido
    ],
)
def test_pagination_params_valid(filter_by, filter_value, should_pass):
    # Act & Assert
    if should_pass:
        params = PaginationParamsDTO(filter_by=filter_by, filter_value=filter_value)
        assert params.filter_by == filter_by
        assert params.filter_value == filter_value
    else:
        with pytest.raises(ValidationError):
            PaginationParamsDTO(filter_by=filter_by, filter_value=filter_value)


@pytest.mark.parametrize(
    ('filter_by', 'filter_value', 'expected_msg'),
    [
        # filter_by inválido (nota o espaço extra no schema: "dos  seguintes")
        (
            'invalid',
            None,
            'O campo filter_by deve ser um dos  seguintes:',
        ),
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
        PaginationParamsDTO(filter_by=filter_by, filter_value=filter_value)

    errors = exc_info.value.errors()
    assert any(expected_msg in error['msg'] for error in errors)


@pytest.mark.parametrize(
    ('kwargs', 'expected_error_type'),
    [
        ({'offset': -1}, 'greater_than_equal'),
        ({'limit': 0}, 'greater_than_equal'),
        ({'limit': 101}, 'less_than_equal'),
        ({'page': 0}, 'greater_than_equal'),
    ],
)
def test_pagination_params_invalid_paging_fields(kwargs, expected_error_type):
    with pytest.raises(ValidationError) as exc_info:
        PaginationParamsDTO(**kwargs)

    errors = exc_info.value.errors()
    assert any(expected_error_type == error['type'] for error in errors)
