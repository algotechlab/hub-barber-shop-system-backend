from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.cash_register import (
    CashRegisterAdjustmentCreateDTO,
    CashRegisterSessionOutDTO,
    CloseCashRegisterSessionDTO,
    OpenCashRegisterSessionDTO,
)
from src.domain.exceptions.cash_register import CashRegisterOpenSessionExistsException
from src.infrastructure.database.models.commom.cash_movement_kind import (
    CashMovementKind,
)
from src.infrastructure.repositories.cash_register_postgres import (
    CashRegisterRepositoryPostgres,
    _money,
)


@pytest.mark.unit
class TestCashRegisterRepositoryPostgres:
    @pytest.fixture
    def mock_session(self):
        session = AsyncMock(spec=AsyncSession)
        session.add = MagicMock()
        return session

    @pytest.fixture
    def repo(self, mock_session):
        return CashRegisterRepositoryPostgres(session=mock_session)

    def test_money_handles_none_and_quantizes(self):
        assert _money(None) == Decimal('0.00')
        assert _money('12.345') == Decimal('12.34')

    async def test_get_open_session_returns_none(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        assert await repo.get_open_session(uuid4()) is None

    async def test_open_session_raises_on_integrity_error(self, repo, mock_session):
        mock_session.commit = AsyncMock(side_effect=IntegrityError('a', 'b', 'c'))
        mock_session.rollback = AsyncMock()
        payload = OpenCashRegisterSessionDTO(
            company_id=uuid4(),
            opened_by=uuid4(),
            opening_balance=Decimal('1'),
        )

        with pytest.raises(CashRegisterOpenSessionExistsException):
            await repo.open_session(payload)

        mock_session.rollback.assert_awaited()

    async def test_list_recent_sessions_returns_dtos(self, repo, mock_session):
        now = datetime.now(timezone.utc)
        row = MagicMock()
        row.id = uuid4()
        row.company_id = uuid4()
        row.opened_by = uuid4()
        row.closed_by = None
        row.opened_at = now
        row.closed_at = None
        row.opening_balance = Decimal('10')
        row.closing_balance = None
        row.expected_balance = None
        row.opening_notes = None
        row.closing_notes = None
        row.created_at = now
        row.updated_at = now
        row.is_deleted = False

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [row]
        mock_session.execute = AsyncMock(return_value=mock_result)

        out = await repo.list_recent_sessions(uuid4(), 10)

        assert len(out) == 1
        assert out[0].id == row.id

    async def test_create_adjustment_commits(self, repo, mock_session):
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch(
            'src.infrastructure.repositories.cash_register_postgres.CashRegisterAdjustment'
        ) as adj_cls:
            mock_row = MagicMock()
            mock_row.id = uuid4()
            mock_row.session_id = uuid4()
            mock_row.company_id = uuid4()
            mock_row.created_by = uuid4()
            mock_row.kind = CashMovementKind.supply
            mock_row.amount = Decimal('5')
            mock_row.description = 'd'
            mock_row.created_at = datetime.now(timezone.utc)
            mock_row.updated_at = datetime.now(timezone.utc)
            mock_row.is_deleted = False
            adj_cls.return_value = mock_row

            payload = CashRegisterAdjustmentCreateDTO(
                session_id=mock_row.session_id,
                company_id=mock_row.company_id,
                created_by=mock_row.created_by,
                kind=CashMovementKind.supply,
                amount=Decimal('5'),
                description='d',
            )
            result = await repo.create_adjustment(payload)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        assert result.amount == Decimal('5')

    async def test_close_session_returns_none_when_missing(self, repo, mock_session):
        mock_session.execute = AsyncMock(
            side_effect=[
                MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
            ]
        )
        payload = CloseCashRegisterSessionDTO(
            session_id=uuid4(),
            company_id=uuid4(),
            closed_by=uuid4(),
            closing_balance=Decimal('1'),
        )

        assert await repo.close_session(payload) is None

    async def test_build_summary_rollback_on_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('fail'))
        mock_session.rollback = AsyncMock()
        now = datetime.now(timezone.utc)
        session = CashRegisterSessionOutDTO(
            id=uuid4(),
            company_id=uuid4(),
            opened_by=uuid4(),
            closed_by=None,
            opened_at=now,
            closed_at=None,
            opening_balance=Decimal('0'),
            closing_balance=None,
            expected_balance=None,
            opening_notes=None,
            closing_notes=None,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )

        with pytest.raises(DatabaseException, match='fail'):
            await repo.build_summary(session, None)

    async def test_open_session_success(self, repo, mock_session):
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        payload = OpenCashRegisterSessionDTO(
            company_id=uuid4(),
            opened_by=uuid4(),
            opening_balance=Decimal('10'),
        )
        expected = MagicMock()
        with patch(
            'src.infrastructure.repositories.cash_register_postgres.CashRegisterSession'
        ):
            with patch.object(
                CashRegisterSessionOutDTO, 'model_validate', return_value=expected
            ):
                result = await repo.open_session(payload)
        assert result == expected

    async def test_open_session_raises_database_exception(self, repo, mock_session):
        mock_session.commit = AsyncMock(side_effect=RuntimeError('fail'))
        mock_session.rollback = AsyncMock()
        payload = OpenCashRegisterSessionDTO(
            company_id=uuid4(),
            opened_by=uuid4(),
            opening_balance=Decimal('1'),
        )
        with patch(
            'src.infrastructure.repositories.cash_register_postgres.CashRegisterSession'
        ):
            with pytest.raises(DatabaseException, match='fail'):
                await repo.open_session(payload)

    async def test_get_open_session_returns_dto(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        expected = MagicMock()
        with patch.object(
            CashRegisterSessionOutDTO, 'model_validate', return_value=expected
        ):
            out = await repo.get_open_session(uuid4())
        assert out == expected

    async def test_get_open_session_execute_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('bad'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='bad'):
            await repo.get_open_session(uuid4())

    async def test_get_session_by_id_returns_none(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        assert await repo.get_session_by_id(uuid4(), uuid4()) is None

    async def test_get_session_by_id_returns_dto(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        expected = MagicMock()
        with patch.object(
            CashRegisterSessionOutDTO, 'model_validate', return_value=expected
        ):
            out = await repo.get_session_by_id(uuid4(), uuid4())
        assert out == expected

    async def test_get_session_by_id_execute_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('x'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='x'):
            await repo.get_session_by_id(uuid4(), uuid4())

    async def test_build_summary_success(self, repo, mock_session):
        amounts = iter([Decimal('10'), Decimal('2'), Decimal('1'), Decimal('3')])

        async def exec_side_effect(*a, **kw):
            m = MagicMock()
            m.scalar_one.return_value = next(amounts)
            return m

        mock_session.execute = AsyncMock(side_effect=exec_side_effect)
        now = datetime.now(timezone.utc)
        session = CashRegisterSessionOutDTO(
            id=uuid4(),
            company_id=uuid4(),
            opened_by=uuid4(),
            closed_by=None,
            opened_at=now,
            closed_at=None,
            opening_balance=Decimal('100'),
            closing_balance=None,
            expected_balance=None,
            opening_notes=None,
            closing_notes=None,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )
        out = await repo.build_summary(session, None)
        assert out.sales_total == Decimal('10')
        assert out.expected_balance == Decimal('106')

    async def test_close_session_row_already_closed(self, repo, mock_session):
        row = MagicMock()
        row.closed_at = datetime.now(timezone.utc)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = row
        mock_session.execute = AsyncMock(return_value=mock_result)
        payload = CloseCashRegisterSessionDTO(
            session_id=uuid4(),
            company_id=uuid4(),
            closed_by=uuid4(),
            closing_balance=Decimal('1'),
        )
        assert await repo.close_session(payload) is None

    async def test_close_session_success(self, repo, mock_session):
        now = datetime.now(timezone.utc)
        row = MagicMock()
        row.closed_at = None
        session_dto = CashRegisterSessionOutDTO(
            id=uuid4(),
            company_id=uuid4(),
            opened_by=uuid4(),
            closed_by=None,
            opened_at=now,
            closed_at=None,
            opening_balance=Decimal('0'),
            closing_balance=None,
            expected_balance=None,
            opening_notes=None,
            closing_notes=None,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )
        closed_dto = session_dto.model_copy(
            update={
                'closed_at': now,
                'closing_balance': Decimal('5'),
                'expected_balance': Decimal('5'),
            }
        )
        first = MagicMock()
        first.scalar_one_or_none.return_value = row
        updated_row = MagicMock()
        second = MagicMock()
        second.scalar_one_or_none.return_value = updated_row
        mock_session.execute = AsyncMock(side_effect=[first, second])
        mock_session.commit = AsyncMock()
        summary_mock = MagicMock()
        summary_mock.expected_balance = Decimal('5')

        with patch.object(
            CashRegisterSessionOutDTO,
            'model_validate',
            side_effect=[session_dto, closed_dto],
        ):
            with patch.object(
                repo, 'build_summary', new_callable=AsyncMock, return_value=summary_mock
            ):
                payload = CloseCashRegisterSessionDTO(
                    session_id=session_dto.id,
                    company_id=session_dto.company_id,
                    closed_by=uuid4(),
                    closing_balance=Decimal('5'),
                )
                result = await repo.close_session(payload)

        assert result == closed_dto

    async def test_close_session_update_returns_none(self, repo, mock_session):
        now = datetime.now(timezone.utc)
        row = MagicMock()
        row.closed_at = None
        session_dto = CashRegisterSessionOutDTO(
            id=uuid4(),
            company_id=uuid4(),
            opened_by=uuid4(),
            closed_by=None,
            opened_at=now,
            closed_at=None,
            opening_balance=Decimal('0'),
            closing_balance=None,
            expected_balance=None,
            opening_notes=None,
            closing_notes=None,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )
        first = MagicMock()
        first.scalar_one_or_none.return_value = row
        second = MagicMock()
        second.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(side_effect=[first, second])
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        summary_mock = MagicMock()
        summary_mock.expected_balance = Decimal('1')
        with patch.object(
            CashRegisterSessionOutDTO, 'model_validate', return_value=session_dto
        ):
            with patch.object(
                repo, 'build_summary', new_callable=AsyncMock, return_value=summary_mock
            ):
                payload = CloseCashRegisterSessionDTO(
                    session_id=session_dto.id,
                    company_id=session_dto.company_id,
                    closed_by=uuid4(),
                    closing_balance=Decimal('1'),
                )
                assert await repo.close_session(payload) is None

        mock_session.rollback.assert_awaited()

    async def test_close_session_execute_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('e'))
        mock_session.rollback = AsyncMock()
        payload = CloseCashRegisterSessionDTO(
            session_id=uuid4(),
            company_id=uuid4(),
            closed_by=uuid4(),
            closing_balance=Decimal('1'),
        )
        with pytest.raises(DatabaseException, match='e'):
            await repo.close_session(payload)

    async def test_list_recent_sessions_execute_error(self, repo, mock_session):
        mock_session.execute = AsyncMock(side_effect=ValueError('z'))
        mock_session.rollback = AsyncMock()
        with pytest.raises(DatabaseException, match='z'):
            await repo.list_recent_sessions(uuid4())

    async def test_create_adjustment_execute_error(self, repo, mock_session):
        mock_session.commit = AsyncMock(side_effect=ValueError('z'))
        mock_session.rollback = AsyncMock()
        payload = CashRegisterAdjustmentCreateDTO(
            session_id=uuid4(),
            company_id=uuid4(),
            created_by=uuid4(),
            kind=CashMovementKind.supply,
            amount=Decimal('1'),
            description='d',
        )
        with patch(
            'src.infrastructure.repositories.cash_register_postgres.CashRegisterAdjustment'
        ):
            with pytest.raises(DatabaseException, match='z'):
                await repo.create_adjustment(payload)
