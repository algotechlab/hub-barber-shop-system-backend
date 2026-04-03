from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.company import CompanyDTO, CreateCompanyDTO
from src.infrastructure.repositories.company_postgres import CompanyRepositoryPostgres

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def repo(mock_session):
    return CompanyRepositoryPostgres(session=mock_session)


@pytest.mark.asyncio
async def test_check_if_company_exists_returns_true_when_found(repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = MagicMock()
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await repo.check_if_company_exists('slug')

    assert result is True


@pytest.mark.asyncio
async def test_check_if_company_exists_rollback_on_error(repo, mock_session):
    mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
    mock_session.rollback = AsyncMock()

    with pytest.raises(DatabaseException, match='DB error'):
        await repo.check_if_company_exists('slug')

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_company_success(repo, mock_session):
    now = datetime.now(timezone.utc)
    dto = CreateCompanyDTO(
        name='N',
        slug='s',
        is_active=True,
        owner_id=uuid4(),
    )
    mock_orm_company = MagicMock()
    mock_orm_company.id = uuid4()
    mock_orm_company.name = dto.name
    mock_orm_company.slug = dto.slug
    mock_orm_company.is_active = dto.is_active
    mock_orm_company.owner_id = dto.owner_id
    mock_orm_company.created_at = now
    mock_orm_company.updated_at = now

    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    expected_dto = MagicMock()
    with (
        patch(
            'src.infrastructure.repositories.company_postgres.Company',
            return_value=mock_orm_company,
        ),
        patch.object(CompanyDTO, 'model_validate', return_value=expected_dto) as mv,
    ):
        result = await repo.create_company(dto)

    mock_session.add.assert_called_once_with(mock_orm_company)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(mock_orm_company)
    mv.assert_called_once_with(mock_orm_company)
    assert result == expected_dto


@pytest.mark.asyncio
async def test_create_company_rollback_on_error(repo, mock_session):
    dto = CreateCompanyDTO(
        name='N',
        slug='s',
        is_active=True,
        owner_id=uuid4(),
    )
    mock_session.add = MagicMock(side_effect=ValueError('DB error'))
    mock_session.rollback = AsyncMock()

    with pytest.raises(DatabaseException, match='DB error'):
        await repo.create_company(dto)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_company_returns_none_when_not_found(repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await repo.get_company(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_get_company_success(repo, mock_session):
    mock_orm_company = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_orm_company
    mock_session.execute = AsyncMock(return_value=mock_result)

    expected_dto = MagicMock()
    with patch.object(CompanyDTO, 'model_validate', return_value=expected_dto) as mv:
        result = await repo.get_company(uuid4())

    mv.assert_called_once_with(mock_orm_company)
    assert result == expected_dto


@pytest.mark.asyncio
async def test_get_company_rollbacks_on_exception(repo, mock_session):
    mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
    mock_session.rollback = AsyncMock()

    result = await repo.get_company(uuid4())

    assert result is None
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_companies_success(repo, mock_session):
    mock_orm_companies = [MagicMock(), MagicMock()]
    mock_scalar_result = MagicMock()
    mock_scalar_result.all.return_value = mock_orm_companies
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalar_result
    mock_session.execute = AsyncMock(return_value=mock_result)

    expected_dtos = [MagicMock(), MagicMock()]
    with patch.object(CompanyDTO, 'model_validate', side_effect=expected_dtos) as mv:
        result = await repo.list_companies(PaginationParamsDTO())

    assert result == expected_dtos
    assert mv.call_count == len(mock_orm_companies)


@pytest.mark.asyncio
async def test_list_companies_rollback_on_error(repo, mock_session):
    mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
    mock_session.rollback = AsyncMock()

    with pytest.raises(DatabaseException, match='DB error'):
        await repo.list_companies(PaginationParamsDTO())

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_companies_applies_filter_when_params_present(repo, mock_session):
    class _DummyCol:
        def __init__(self, name: str):
            self.name = name

        def __eq__(self, other):
            return ('eq', self.name, other)

        __hash__ = None

        def ilike(self, pattern: str):
            return ('ilike', self.name, pattern)

        def desc(self):
            return ('desc', self.name)

    class _DummyCompany:
        is_deleted = _DummyCol('is_deleted')
        created_at = _DummyCol('created_at')
        name = _DummyCol('name')

    class _FakeQuery:
        def __init__(self):
            self.where_args = []
            self.filter_args = []
            self.order_by_args = []
            self.offset_value = None
            self.limit_value = None

        def where(self, *args):
            self.where_args.extend(args)
            return self

        def filter(self, *args):
            self.filter_args.extend(args)
            return self

        def order_by(self, *args):
            self.order_by_args.extend(args)
            return self

        def offset(self, value):
            self.offset_value = value
            return self

        def limit(self, value):
            self.limit_value = value
            return self

    fake_query = _FakeQuery()

    def _fake_select(_model):  # noqa: ANN001
        return fake_query

    pagination = PaginationParamsDTO(filter_by='name', filter_value='John')

    mock_orm_companies = [MagicMock()]
    mock_scalar_result = MagicMock()
    mock_scalar_result.all.return_value = mock_orm_companies
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalar_result
    mock_session.execute = AsyncMock(return_value=mock_result)

    expected_dtos = [MagicMock()]
    with (
        patch('src.infrastructure.repositories.company_postgres.select', _fake_select),
        patch(
            'src.infrastructure.repositories.company_postgres.Company', _DummyCompany
        ),
        patch.object(CompanyDTO, 'model_validate', side_effect=expected_dtos),
    ):
        result = await repo.list_companies(pagination)

    assert ('ilike', 'name', '%John%') in fake_query.filter_args
    assert ('desc', 'created_at') in fake_query.order_by_args
    assert fake_query.offset_value == pagination.offset
    assert fake_query.limit_value == pagination.limit
    mock_session.execute.assert_awaited_once_with(fake_query)
    assert result == expected_dtos


@pytest.mark.asyncio
async def test_delete_company_returns_true_when_updated(repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = MagicMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()

    result = await repo.delete_company(uuid4())

    assert result is True
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_company_returns_false_when_not_found(repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()

    result = await repo.delete_company(uuid4())

    assert result is False
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_company_rollback_on_error(repo, mock_session):
    mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
    mock_session.rollback = AsyncMock()

    with pytest.raises(DatabaseException, match='DB error'):
        await repo.delete_company(uuid4())

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_companies_slug_success(repo, mock_session):
    mock_orm_companies = [MagicMock(), MagicMock()]
    mock_scalar_result = MagicMock()
    mock_scalar_result.all.return_value = mock_orm_companies
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalar_result
    mock_session.execute = AsyncMock(return_value=mock_result)

    expected_dtos = [MagicMock(), MagicMock()]
    with patch.object(CompanyDTO, 'model_validate', side_effect=expected_dtos) as mv:
        result = await repo.list_companies_slug('slug-x')

    assert result == expected_dtos
    assert mv.call_count == len(mock_orm_companies)


@pytest.mark.asyncio
async def test_list_companies_slug_rollback_on_error(repo, mock_session):
    mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
    mock_session.rollback = AsyncMock()

    with pytest.raises(DatabaseException, match='DB error'):
        await repo.list_companies_slug('slug-x')

    mock_session.rollback.assert_awaited_once()
