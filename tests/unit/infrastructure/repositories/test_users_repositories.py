from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.auth import UserAuthDTO
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.users import UpdateUserDTO, UserBaseDTO, UserOutDTO
from src.infrastructure.repositories.users_postgres import UsersRepositoryPostgres


@pytest.mark.unit
class TestUsersRepositoryPostgres:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session):
        return UsersRepositoryPostgres(session=mock_session)

    async def test_create_user_success(self, repo, mock_session):
        company_id = uuid4()
        user_dto = UserBaseDTO(
            name='Test User',
            email='test@example.com',
            password='hashed',
            phone='11999999999',
            company_id=company_id,
        )
        now = datetime.now(timezone.utc)
        mock_orm_user = MagicMock()
        mock_orm_user.id = uuid4()
        mock_orm_user.name = user_dto.name
        mock_orm_user.email = user_dto.email
        mock_orm_user.phone = user_dto.phone
        mock_orm_user.password = user_dto.password
        mock_orm_user.company_id = company_id
        mock_orm_user.is_active = True
        mock_orm_user.created_at = now
        mock_orm_user.updated_at = now
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch(
            'src.infrastructure.repositories.users_postgres.User',
            return_value=mock_orm_user,
        ):
            result = await repo.create_user(user_dto)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()
        assert result.name == user_dto.name
        assert result.email == user_dto.email
        assert result.id == mock_orm_user.id

    async def test_list_users_success(self, repo, mock_session):
        pagination = PaginationParamsDTO()
        mock_orm_users = [MagicMock(), MagicMock()]
        mock_scalar_result = MagicMock()
        mock_scalar_result.all.return_value = mock_orm_users

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected_dtos = [MagicMock(), MagicMock()]
        with patch.object(
            UserOutDTO, 'model_validate', side_effect=expected_dtos
        ) as mock_model_validate:
            result = await repo.list_users(pagination)

        assert result == expected_dtos
        assert mock_model_validate.call_count == len(mock_orm_users)

    async def test_list_users_applies_filter_when_params_present(
        self, repo, mock_session
    ):
        class _DummyCol:
            def __init__(self, name: str):
                self.name = name

            def __eq__(self, other):  # noqa: D105
                return ('eq', self.name, other)

        class _DummyUser:
            is_deleted = _DummyCol('is_deleted')
            created_at = object()
            name = _DummyCol('name')

        class _FakeQuery:
            def __init__(self):
                self.where_args = []
                self.order_by_args = []
                self.filter_args = []

            def where(self, *args):
                self.where_args.extend(args)
                return self

            def order_by(self, *args):
                self.order_by_args.extend(args)
                return self

            def filter(self, *args):
                self.filter_args.extend(args)
                return self

        fake_query = _FakeQuery()

        def _fake_select(_model):
            # o repositório chama select(User) e encadeia where/order_by/filter
            return fake_query

        pagination = PaginationParamsDTO(filter_by='name', filter_value='John')
        mock_orm_users = [MagicMock()]
        mock_scalar_result = MagicMock()
        mock_scalar_result.all.return_value = mock_orm_users
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected_dtos = [MagicMock()]
        with (
            patch(
                'src.infrastructure.repositories.users_postgres.select', _fake_select
            ),
            patch('src.infrastructure.repositories.users_postgres.User', _DummyUser),
            patch.object(UserOutDTO, 'model_validate', side_effect=expected_dtos),
        ):
            result = await repo.list_users(pagination)

        # garante que o filtro foi aplicado com o campo e valor corretos
        assert ('eq', 'name', 'John') in fake_query.filter_args
        # e que a query filtrada foi a que foi executada
        mock_session.execute.assert_awaited_once_with(fake_query)
        assert result == expected_dtos

    async def test_list_users_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.list_users(PaginationParamsDTO())

        mock_session.rollback.assert_awaited_once()

    async def test_create_user_rollback_on_error(self, repo, mock_session):
        mock_session.add = MagicMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()
        user_dto = UserBaseDTO(
            name='Test',
            email='test@example.com',
            password='hash',
            phone='11999999999',
            company_id=uuid4(),
        )

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.create_user(user_dto)

        mock_session.rollback.assert_awaited_once()

    async def test_get_user_returns_none_when_not_found(self, repo, mock_session):
        from sqlalchemy.engine import Result

        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user(uuid4())

        assert result is None

    async def test_get_user_success(self, repo, mock_session):
        from sqlalchemy.engine import Result

        mock_orm_user = MagicMock()
        expected_dto = MagicMock()

        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = mock_orm_user
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch.object(
            UserOutDTO, 'model_validate', return_value=expected_dto
        ) as mv:
            result = await repo.get_user(uuid4())

        mv.assert_called_once_with(mock_orm_user)
        assert result == expected_dto

    async def test_get_user_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_user(uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_get_user_auth_by_phone_returns_none_when_not_found(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_auth_by_phone('11999999999')

        assert result is None

    async def test_get_user_auth_by_phone_success(self, repo, mock_session):
        mock_orm_user = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_orm_user
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected_dto = MagicMock()
        with patch.object(
            UserAuthDTO, 'model_validate', return_value=expected_dto
        ) as mv:
            result = await repo.get_user_auth_by_phone('11999999999')

        mv.assert_called_once_with(mock_orm_user)
        assert result == expected_dto

    async def test_get_user_auth_by_phone_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_user_auth_by_phone('11999999999')

        mock_session.rollback.assert_awaited_once()

    async def test_update_user_returns_none_when_not_found(self, repo, mock_session):
        from sqlalchemy.engine import Result

        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.update_user(uuid4(), UpdateUserDTO(name='X'))

        assert result is None
        mock_session.commit.assert_awaited_once()

    async def test_update_user_success(self, repo, mock_session):
        from sqlalchemy.engine import Result

        mock_updated_orm = MagicMock()
        expected_dto = MagicMock()

        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = mock_updated_orm
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        with patch.object(
            UserOutDTO, 'model_validate', return_value=expected_dto
        ) as mv:
            result = await repo.update_user(uuid4(), UpdateUserDTO(name='Updated'))

        mock_session.commit.assert_awaited_once()
        mv.assert_called_once_with(mock_updated_orm)
        assert result == expected_dto

    async def test_update_user_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.update_user(uuid4(), UpdateUserDTO(name='Updated'))

        mock_session.rollback.assert_awaited_once()

    async def test_delete_user_success_returns_true(self, repo, mock_session):
        from sqlalchemy.engine import Result

        mock_user = MagicMock()
        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_user(uuid4())

        assert result is True
        mock_session.commit.assert_awaited_once()

    async def test_delete_user_not_found_returns_false(self, repo, mock_session):
        from sqlalchemy.engine import Result

        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_user(uuid4())

        assert result is False

    async def test_delete_user_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.delete_user(uuid4())

        mock_session.rollback.assert_awaited_once()
