import pytest
from pydantic import ValidationError
from src.interface.api.v1.schema.common.pagination import PaginationParamsBaseSchema

pytestmark = pytest.mark.unit

# ---------------------------------------------------------------------------
# Casos válidos
# ---------------------------------------------------------------------------


def test_pagination_params_base_schema_default():
    """
    Instância sem argumentos deve usar
    defaults None para filter_by e filter_value.
    """
    schema = PaginationParamsBaseSchema()
    assert schema.filter_by is None
    assert schema.filter_value is None


@pytest.mark.parametrize(
    ('filter_by', 'filter_value'),
    [
        (None, None),
        ('username', 'john'),
        ('username', '123'),
        ('name', 'João Silva'),
        ('document', '12345678900'),
        ('description', 'algum texto'),
    ],
)
def test_pagination_params_valid(filter_by, filter_value):
    """filter_by permitidos com filter_value devem ser aceitos."""
    schema = PaginationParamsBaseSchema(filter_by=filter_by, filter_value=filter_value)
    assert schema.filter_by == filter_by
    assert schema.filter_value == filter_value


@pytest.mark.parametrize(
    'allowed_field',
    ['username', 'name', 'document', 'description'],
)
def test_pagination_params_all_allowed_filter_by(allowed_field):
    """Todos os campos permitidos em filter_by devem ser aceitos."""
    schema = PaginationParamsBaseSchema(
        filter_by=allowed_field, filter_value='qualquer'
    )
    assert schema.filter_by == allowed_field
    assert schema.filter_value == 'qualquer'


# ---------------------------------------------------------------------------
# filter_by inválido
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    'invalid_filter_by',
    ['email', 'id', 'invalid', '', 'USERNAME'],
)
def test_pagination_params_invalid_filter_by(invalid_filter_by):
    """filter_by fora da lista permitida deve levantar ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        PaginationParamsBaseSchema(filter_by=invalid_filter_by, filter_value='valor')

    errors = exc_info.value.errors()
    assert any('filter_by' in str(e.get('loc', [])) for e in errors)
    assert any('seguintes' in error.get('msg', '') for error in errors)


# ---------------------------------------------------------------------------
# Par filter_by / filter_value inconsistente
# ---------------------------------------------------------------------------


def test_pagination_params_filter_by_without_filter_value():
    """filter_by definido sem filter_value deve levantar ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        PaginationParamsBaseSchema(filter_by='username', filter_value=None)

    errors = exc_info.value.errors()
    assert any(
        'filter_by' in error.get('msg', '')
        and 'filter_value' in error.get('msg', '')
        or 'filter_value' in error.get('msg', '')
        for error in errors
    )
    assert any('definiu filter_by' in error.get('msg', '') for error in errors)


def test_pagination_params_filter_value_without_filter_by():
    """filter_value definido sem filter_by deve levantar ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        PaginationParamsBaseSchema(filter_by=None, filter_value='john')

    errors = exc_info.value.errors()
    assert any(
        'filter_value' in error.get('msg', '')
        and 'filter_by' in error.get('msg', '')
        or 'filter_by' in error.get('msg', '')
        for error in errors
    )
    assert any('enviou um valor de busca' in error.get('msg', '') for error in errors)


# ---------------------------------------------------------------------------
# Model_validator retorna self
# ---------------------------------------------------------------------------


def test_pagination_params_check_filter_pair_returns_self():
    """Após validação bem-sucedida, a instância deve ser retornada intacta."""
    schema = PaginationParamsBaseSchema(filter_by='name', filter_value='test')
    assert schema.filter_by == 'name'
    assert schema.filter_value == 'test'
