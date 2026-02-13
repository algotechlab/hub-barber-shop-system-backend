from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.auth import OwnerAuthDTO
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.owner import OwnerOutDTO, UpdateOwnerDTO
from src.infrastructure.repositories.owner_postgres import OwnerRepositoryPostgres


@pytest.mark.unit
class TestOwnerRepositoryPostgres:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session):
        return OwnerRepositoryPostgres(session=mock_session)

    async def test_create_owner_success(self, repo, mock_session, owner_create_dto):
        now = datetime.now(timezone.utc)
        mock_orm_owner = MagicMock()
        mock_orm_owner.id = uuid4()
        mock_orm_owner.name = owner_create_dto.name
        mock_orm_owner.email = owner_create_dto.email
        mock_orm_owner.password = owner_create_dto.password
        mock_orm_owner.phone = owner_create_dto.phone
        mock_orm_owner.created_at = now
        mock_orm_owner.updated_at = now

        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        expected_dto = MagicMock()
        with (
            patch(
                'src.infrastructure.repositories.owner_postgres.Owner',
                return_value=mock_orm_owner,
            ),
            patch.object(
                OwnerOutDTO, 'model_validate', return_value=expected_dto
            ) as mv,
        ):
            result = await repo.create_owner(owner_create_dto)

        mock_session.add.assert_called_once_with(mock_orm_owner)
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(mock_orm_owner)
        mv.assert_called_once_with(mock_orm_owner)
        assert result == expected_dto

    async def test_create_owner_rollback_on_error(
        self, repo, mock_session, owner_create_dto
    ):
        mock_session.add = MagicMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.create_owner(owner_create_dto)

        mock_session.rollback.assert_awaited_once()

    async def test_get_owner_returns_none_when_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_owner(uuid4())

        assert result is None

    async def test_get_owner_success(self, repo, mock_session):
        mock_orm_owner = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_orm_owner
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected_dto = MagicMock()
        with patch.object(
            OwnerOutDTO, 'model_validate', return_value=expected_dto
        ) as mv:
            result = await repo.get_owner(uuid4())

        mv.assert_called_once_with(mock_orm_owner)
        assert result == expected_dto

    async def test_get_owner_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_owner(uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_get_owner_by_email_returns_none_when_not_found(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_owner_by_email('john@example.com')

        assert result is None

    async def test_get_owner_by_email_success(self, repo, mock_session):
        mock_orm_owner = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_orm_owner
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected_dto = MagicMock()
        with patch.object(
            OwnerOutDTO, 'model_validate', return_value=expected_dto
        ) as mv:
            result = await repo.get_owner_by_email('john@example.com')

        mv.assert_called_once_with(mock_orm_owner)
        assert result == expected_dto

    async def test_get_owner_by_email_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_owner_by_email('john@example.com')

        mock_session.rollback.assert_awaited_once()

    async def test_get_owner_auth_by_email_returns_none_when_not_found(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_owner_auth_by_email('john@example.com')

        assert result is None

    async def test_get_owner_auth_by_email_success(self, repo, mock_session):
        mock_orm_owner = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_orm_owner
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected_dto = MagicMock()
        with patch.object(
            OwnerAuthDTO, 'model_validate', return_value=expected_dto
        ) as mv:
            result = await repo.get_owner_auth_by_email('john@example.com')

        mv.assert_called_once_with(mock_orm_owner)
        assert result == expected_dto

    async def test_get_owner_auth_by_email_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_owner_auth_by_email('john@example.com')

        mock_session.rollback.assert_awaited_once()

    async def test_list_owners_success(self, repo, mock_session):
        pagination = PaginationParamsDTO()
        mock_orm_owners = [MagicMock(), MagicMock()]
        mock_scalar_result = MagicMock()
        mock_scalar_result.all.return_value = mock_orm_owners

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected_dtos = [MagicMock(), MagicMock()]
        with patch.object(
            OwnerOutDTO, 'model_validate', side_effect=expected_dtos
        ) as mv:
            result = await repo.list_owners(pagination)

        assert result == expected_dtos
        assert mv.call_count == len(mock_orm_owners)

    async def test_list_owners_applies_filter_when_params_present(
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

        class _DummyOwner:
            is_deleted = _DummyCol('is_deleted')
            name = _DummyCol('name')
            created_at = _DummyCol('created_at')

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

        def _fake_select(_model):
            return fake_query

        pagination = PaginationParamsDTO(filter_by='name', filter_value='John')

        mock_orm_owners = [MagicMock()]
        mock_scalar_result = MagicMock()
        mock_scalar_result.all.return_value = mock_orm_owners
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected_dtos = [MagicMock()]
        with (
            patch(
                'src.infrastructure.repositories.owner_postgres.select', _fake_select
            ),
            patch('src.infrastructure.repositories.owner_postgres.Owner', _DummyOwner),
            patch.object(OwnerOutDTO, 'model_validate', side_effect=expected_dtos),
        ):
            result = await repo.list_owners(pagination)

        assert ('ilike', 'name', '%John%') in fake_query.filter_args
        assert ('desc', 'created_at') in fake_query.order_by_args
        assert fake_query.offset_value == pagination.offset
        assert fake_query.limit_value == pagination.limit
        mock_session.execute.assert_awaited_once_with(fake_query)
        assert result == expected_dtos

    async def test_list_owners_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.list_owners(PaginationParamsDTO())

        mock_session.rollback.assert_awaited_once()

    async def test_update_owner_returns_none_when_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.update_owner(uuid4(), UpdateOwnerDTO(name='X'))

        assert result is None
        mock_session.commit.assert_awaited_once()

    async def test_update_owner_success(self, repo, mock_session):
        mock_updated_orm = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_updated_orm
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        expected_dto = MagicMock()
        with patch.object(
            OwnerOutDTO, 'model_validate', return_value=expected_dto
        ) as mv:
            result = await repo.update_owner(uuid4(), UpdateOwnerDTO(name='Updated'))

        mock_session.commit.assert_awaited_once()
        mv.assert_called_once_with(mock_updated_orm)
        assert result == expected_dto

    async def test_update_owner_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.update_owner(uuid4(), UpdateOwnerDTO(name='Updated'))

        mock_session.rollback.assert_awaited_once()

    async def test_delete_owner_returns_true_when_updated(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_owner(uuid4())

        assert result is True
        mock_session.commit.assert_awaited_once()

    async def test_delete_owner_returns_false_when_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_owner(uuid4())

        assert result is False
        mock_session.commit.assert_awaited_once()

    async def test_delete_owner_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.delete_owner(uuid4())

        mock_session.rollback.assert_awaited_once()
