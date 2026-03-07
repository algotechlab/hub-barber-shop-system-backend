from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.auth import EmployeeAuthDTO
from src.domain.dtos.common.pagination import PaginationParamsDTO
from src.domain.dtos.employee import EmployeeBaseDTO, EmployeeOutDTO, UpdateEmployeeDTO
from src.infrastructure.repositories.employee_postgres import EmployeeRepositoryPostgres


@pytest.mark.unit
class TestEmployeeRepositoryPostgres:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session):
        return EmployeeRepositoryPostgres(session=mock_session)

    @pytest.fixture
    def employee_base_dto(self):
        return EmployeeBaseDTO(
            name='John',
            last_name='Doe',
            phone='11999999999',
            password='plain',
            is_active=True,
            role='admin',
            company_id=uuid4(),
        )

    async def test_create_employee_success(self, repo, mock_session, employee_base_dto):
        now = datetime.now(timezone.utc)
        mock_orm_employee = MagicMock()
        mock_orm_employee.id = uuid4()
        mock_orm_employee.name = employee_base_dto.name
        mock_orm_employee.last_name = employee_base_dto.last_name
        mock_orm_employee.phone = employee_base_dto.phone
        mock_orm_employee.password = employee_base_dto.password
        mock_orm_employee.is_active = employee_base_dto.is_active
        mock_orm_employee.role = employee_base_dto.role
        mock_orm_employee.company_id = employee_base_dto.company_id
        mock_orm_employee.created_at = now
        mock_orm_employee.updated_at = now

        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        expected_dto = MagicMock()
        with (
            patch(
                'src.infrastructure.repositories.employee_postgres.Employee',
                return_value=mock_orm_employee,
            ),
            patch.object(
                EmployeeOutDTO, 'model_validate', return_value=expected_dto
            ) as mv,
        ):
            result = await repo.create_employee(employee_base_dto)

        mock_session.add.assert_called_once_with(mock_orm_employee)
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(mock_orm_employee)
        mv.assert_called_once_with(mock_orm_employee)
        assert result == expected_dto

    async def test_create_employee_rollback_on_error(
        self, repo, mock_session, employee_base_dto
    ):
        mock_session.add = MagicMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.create_employee(employee_base_dto)

        mock_session.rollback.assert_awaited_once()

    async def test_get_employee_returns_none_when_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_employee(uuid4(), uuid4())

        assert result is None

    async def test_get_employee_success(self, repo, mock_session):
        mock_orm_employee = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_orm_employee
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected_dto = MagicMock()
        with patch.object(
            EmployeeOutDTO, 'model_validate', return_value=expected_dto
        ) as mv:
            result = await repo.get_employee(uuid4(), uuid4())

        mv.assert_called_once_with(mock_orm_employee)
        assert result == expected_dto

    async def test_get_employee_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_employee(uuid4(), uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_get_employee_auth_by_phone_returns_none_when_not_found(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_employee_auth_by_phone('11999999999')

        assert result is None

    async def test_get_employee_auth_by_phone_success(self, repo, mock_session):
        mock_orm_employee = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_orm_employee
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected_dto = MagicMock()
        with patch.object(
            EmployeeAuthDTO, 'model_validate', return_value=expected_dto
        ) as mv:
            result = await repo.get_employee_auth_by_phone('11999999999')

        mv.assert_called_once_with(mock_orm_employee)
        assert result == expected_dto

    async def test_get_employee_auth_by_phone_rollback_on_error(
        self, repo, mock_session
    ):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.get_employee_auth_by_phone('11999999999')

        mock_session.rollback.assert_awaited_once()

    async def test_list_employees_success(self, repo, mock_session):
        pagination = PaginationParamsDTO()
        company_id = uuid4()
        mock_orm_employees = [MagicMock(), MagicMock()]
        mock_rows = [(mock_orm_employees[0], True), (mock_orm_employees[1], False)]
        mock_result = MagicMock()
        mock_result.all.return_value = mock_rows
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected_dtos = [MagicMock(), MagicMock()]
        with patch.object(
            EmployeeOutDTO, 'model_validate', side_effect=expected_dtos
        ) as mv:
            result = await repo.list_employees(pagination, company_id)

        assert result == expected_dtos
        assert mv.call_count == len(mock_orm_employees)

    async def test_list_employees_applies_filter_when_params_present(
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

        class _DummyEmployee:
            id = _DummyCol('id')
            is_deleted = _DummyCol('is_deleted')
            name = _DummyCol('name')
            company_id = _DummyCol('company_id')
            created_at = _DummyCol('created_at')

        class _FakeQuery:
            def __init__(self):
                self.where_args = []
                self.order_by_args = []
                self.offset_value = None
                self.limit_value = None

            def where(self, *args):
                self.where_args.extend(args)
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

            def exists(self):
                return self

            def label(self, _name):
                return self

        fake_query = _FakeQuery()

        def _fake_select(*_args):
            return fake_query

        pagination = PaginationParamsDTO(filter_by='name', filter_value='John')
        company_id = uuid4()

        mock_orm_employees = [MagicMock()]
        mock_rows = [(mock_orm_employees[0], False)]
        mock_result = MagicMock()
        mock_result.all.return_value = mock_rows
        mock_session.execute = AsyncMock(return_value=mock_result)

        expected_dtos = [MagicMock()]
        with (
            patch(
                'src.infrastructure.repositories.employee_postgres.select', _fake_select
            ),
            patch(
                'src.infrastructure.repositories.employee_postgres.Employee',
                _DummyEmployee,
            ),
            patch.object(EmployeeOutDTO, 'model_validate', side_effect=expected_dtos),
        ):
            result = await repo.list_employees(pagination, company_id)

        assert ('ilike', 'name', '%John%') in fake_query.where_args
        assert ('desc', 'created_at') in fake_query.order_by_args
        assert fake_query.offset_value == pagination.offset
        assert fake_query.limit_value == pagination.limit
        mock_session.execute.assert_awaited_once_with(fake_query)
        assert result == expected_dtos

    async def test_list_employees_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.list_employees(PaginationParamsDTO(), uuid4())

        mock_session.rollback.assert_awaited_once()

    async def test_update_employee_returns_none_when_not_found(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.update_employee(
            uuid4(), UpdateEmployeeDTO(name='X'), uuid4()
        )

        assert result is None
        mock_session.commit.assert_awaited_once()

    async def test_update_employee_success(self, repo, mock_session):
        mock_updated_orm = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_updated_orm
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        expected_dto = MagicMock()
        with patch.object(
            EmployeeOutDTO, 'model_validate', return_value=expected_dto
        ) as mv:
            result = await repo.update_employee(
                uuid4(), UpdateEmployeeDTO(name='Updated'), uuid4()
            )

        mock_session.commit.assert_awaited_once()
        mv.assert_called_once_with(mock_updated_orm)
        assert result == expected_dto

    async def test_update_employee_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.update_employee(
                uuid4(), UpdateEmployeeDTO(name='Updated'), uuid4()
            )

        mock_session.rollback.assert_awaited_once()

    async def test_delete_employee_returns_true_when_rowcount_gt_zero(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_employee(uuid4(), uuid4())

        assert result is True
        mock_session.commit.assert_awaited_once()

    async def test_delete_employee_returns_false_when_rowcount_zero(
        self, repo, mock_session
    ):
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await repo.delete_employee(uuid4(), uuid4())

        assert result is False
        mock_session.commit.assert_awaited_once()

    async def test_delete_employee_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('DB error'))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseException, match='DB error'):
            await repo.delete_employee(uuid4(), uuid4())

        mock_session.rollback.assert_awaited_once()
