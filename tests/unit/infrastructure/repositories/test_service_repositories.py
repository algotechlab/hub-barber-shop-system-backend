from datetime import timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.service import CreateServiceDTO, ServiceDTO, UpdateServiceDTO
from src.infrastructure.repositories.service_postgres import ServiceRepositoryPostgres


@pytest.mark.unit
class TestServiceRepositoryPostgres:
    TIME_TO_SPEND_45 = 45

    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session):
        return ServiceRepositoryPostgres(session=mock_session)

    async def test_create_service_success_converts_interval(self, repo, mock_session):
        company_id = uuid4()
        dto = CreateServiceDTO(
            name='Corte',
            description='Desc',
            price=Decimal('10'),
            duration=30,
            category='Cat',
            time_to_spend=self.TIME_TO_SPEND_45,
            status=True,
            url_image='https://cdn.example.com/a.png',
            company_id=company_id,
        )
        mock_orm = MagicMock()
        mock_orm.id = uuid4()
        mock_orm.name = dto.name
        mock_orm.description = dto.description
        mock_orm.price = dto.price
        mock_orm.duration = dto.duration
        mock_orm.category = dto.category
        mock_orm.time_to_spend = timedelta(minutes=self.TIME_TO_SPEND_45)
        mock_orm.status = dto.status
        mock_orm.url_image = dto.url_image
        mock_orm.company_id = dto.company_id
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch(
            'src.infrastructure.repositories.service_postgres.Service',
            return_value=mock_orm,
        ) as service_model:
            result = await repo.create_service(dto)

        _, kwargs = service_model.call_args
        assert kwargs['time_to_spend'] == timedelta(minutes=self.TIME_TO_SPEND_45)
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()
        assert isinstance(result, ServiceDTO)
        assert result.company_id == company_id
        assert result.time_to_spend == self.TIME_TO_SPEND_45

    async def test_create_service_rollback_on_error(self, repo, mock_session):
        mock_session.add = MagicMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()
        dto = CreateServiceDTO(
            name='Corte',
            description='Desc',
            price=Decimal('10'),
            duration=30,
            category='Cat',
            time_to_spend=30,
            status=True,
            url_image='https://cdn.example.com/a.png',
            company_id=uuid4(),
        )

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.create_service(dto)

        mock_session.rollback.assert_awaited_once()

    async def test_get_service_returns_none_when_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_service(uuid4(), uuid4())

        assert result is None

    async def test_get_service_success(self, repo, mock_session):
        mock_orm = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_orm
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected = MagicMock()
        with patch.object(ServiceDTO, 'model_validate', return_value=expected) as mv:
            result = await repo.get_service(uuid4(), uuid4())

        mv.assert_called_once_with(mock_orm)
        assert result == expected

    async def test_get_service_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_service(uuid4(), uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_list_services_success(self, repo, mock_session):
        mock_orm_services = [MagicMock(), MagicMock()]
        mock_scalar_result = MagicMock()
        mock_scalar_result.all.return_value = mock_orm_services
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected = [MagicMock(), MagicMock()]
        with patch.object(ServiceDTO, 'model_validate', side_effect=expected) as mv:
            result = await repo.list_services(PaginationParamsDTO(), uuid4())

        assert result == expected
        assert mv.call_count == len(mock_orm_services)

    async def test_list_services_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.list_services(PaginationParamsDTO(), uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_list_services_applies_filter_when_params_present(
        self, repo, mock_session
    ):
        class _DummyCol:
            def __init__(self, name: str):
                self.name = name

            def __eq__(self, other):
                return ('eq', self.name, other)

            def ilike(self, pattern: str):
                return ('ilike', self.name, pattern)

            def desc(self):
                return ('desc', self.name)

        class _DummyService:
            is_deleted = _DummyCol('is_deleted')
            company_id = _DummyCol('company_id')
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
        company_id = uuid4()

        mock_orm_services = [MagicMock()]
        mock_scalar_result = MagicMock()
        mock_scalar_result.all.return_value = mock_orm_services
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected_dtos = [MagicMock()]
        with (
            patch(
                'src.infrastructure.repositories.service_postgres.select', _fake_select
            ),
            patch(
                'src.infrastructure.repositories.service_postgres.Service',
                _DummyService,
            ),
            patch.object(ServiceDTO, 'model_validate', side_effect=expected_dtos),
        ):
            result = await repo.list_services(pagination, company_id)

        assert ('ilike', 'name', '%John%') in fake_query.filter_args
        assert ('desc', 'created_at') in fake_query.order_by_args
        assert fake_query.offset_value == pagination.offset
        assert fake_query.limit_value == pagination.limit
        mock_session.execute.assert_awaited_once_with(fake_query)
        assert result == expected_dtos

    async def test_update_service_returns_none_when_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.update_service(uuid4(), UpdateServiceDTO(name='X'), uuid4())

        assert result is None
        mock_session.commit.assert_awaited_once()

    async def test_update_service_success(self, repo, mock_session):
        mock_updated = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_updated
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        expected = MagicMock()
        with patch.object(ServiceDTO, 'model_validate', return_value=expected) as mv:
            result = await repo.update_service(
                uuid4(), UpdateServiceDTO(name='Updated'), uuid4()
            )

        mock_session.commit.assert_awaited_once()
        mv.assert_called_once_with(mock_updated)
        assert result == expected

    async def test_update_service_converts_interval_when_minutes_int(
        self, repo, mock_session
    ):
        seen_stmts = []

        class DummyUpdate:
            def __init__(self):
                self.values_kwargs = None

            def where(self, *args, **kwargs):  # noqa: ANN002, ANN003
                return self

            def values(self, **kwargs):
                self.values_kwargs = kwargs
                return self

            def returning(self, *args, **kwargs):  # noqa: ANN002, ANN003
                return self

        def fake_update(*args, **kwargs):  # noqa: ANN002, ANN003
            stmt = DummyUpdate()
            seen_stmts.append(stmt)
            return stmt

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        with patch(
            'src.infrastructure.repositories.service_postgres.update', fake_update
        ):
            with patch.object(ServiceDTO, 'model_validate', return_value=MagicMock()):
                await repo.update_service(
                    uuid4(),
                    UpdateServiceDTO(time_to_spend=self.TIME_TO_SPEND_45),
                    uuid4(),
                )

        assert seen_stmts, 'expected update() to be called'
        assert seen_stmts[0].values_kwargs['time_to_spend'] == timedelta(
            minutes=self.TIME_TO_SPEND_45
        )

    async def test_update_service_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.update_service(
                uuid4(), UpdateServiceDTO(name='Updated'), uuid4()
            )

        mock_session.rollback.assert_awaited_once()

    async def test_delete_service_returns_true_when_rowcount_positive(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_service(uuid4(), uuid4())

        assert result is True
        mock_session.commit.assert_awaited_once()

    async def test_delete_service_returns_false_when_rowcount_zero(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_service(uuid4(), uuid4())

        assert result is False

    async def test_delete_service_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.delete_service(uuid4(), uuid4())

        mock_session.rollback.assert_awaited_once()
