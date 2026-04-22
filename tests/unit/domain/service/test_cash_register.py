from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.cash_register import (
    CashRegisterAdjustmentCreateDTO,
    CashRegisterSessionOutDTO,
    CashRegisterSummaryDTO,
    CloseCashRegisterSessionDTO,
    OpenCashRegisterSessionDTO,
)
from src.domain.service.cash_register import CashRegisterService
from src.infrastructure.database.models.commom.cash_movement_kind import (
    CashMovementKind,
)


@pytest.mark.unit
class TestCashRegisterService:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository):
        return CashRegisterService(cash_register_repository=mock_repository)

    async def test_open_session_delegates(self, service, mock_repository):
        payload = OpenCashRegisterSessionDTO(
            company_id=uuid4(),
            opened_by=uuid4(),
            opening_balance=Decimal('50'),
        )
        expected = AsyncMock(spec=CashRegisterSessionOutDTO)
        mock_repository.open_session.return_value = expected

        result = await service.open_session(payload)

        mock_repository.open_session.assert_awaited_once_with(payload)
        assert result == expected

    async def test_build_summary_delegates(self, service, mock_repository):
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
        summary = CashRegisterSummaryDTO(
            session=session,
            sales_total=Decimal('1'),
            expenses_total=Decimal('0'),
            supplies_total=Decimal('0'),
            withdrawals_total=Decimal('0'),
            expected_balance=Decimal('1'),
            window_end_at=now,
        )
        mock_repository.build_summary.return_value = summary

        result = await service.build_summary(session, None)

        mock_repository.build_summary.assert_awaited_once_with(session, None)
        assert result == summary

    async def test_create_adjustment_delegates(self, service, mock_repository):
        payload = CashRegisterAdjustmentCreateDTO(
            session_id=uuid4(),
            company_id=uuid4(),
            created_by=uuid4(),
            kind=CashMovementKind.withdrawal,
            amount=Decimal('5'),
            description='sangria',
        )
        expected = AsyncMock()
        mock_repository.create_adjustment.return_value = expected

        result = await service.create_adjustment(payload)

        mock_repository.create_adjustment.assert_awaited_once_with(payload)
        assert result == expected

    async def test_get_open_session_delegates(self, service, mock_repository):
        cid = uuid4()
        mock_repository.get_open_session.return_value = None

        assert await service.get_open_session(cid) is None
        mock_repository.get_open_session.assert_awaited_once_with(cid)

    async def test_get_session_by_id_delegates(self, service, mock_repository):
        sid = uuid4()
        cid = uuid4()
        mock_repository.get_session_by_id.return_value = None

        assert await service.get_session_by_id(sid, cid) is None
        mock_repository.get_session_by_id.assert_awaited_once_with(sid, cid)

    async def test_close_session_delegates(self, service, mock_repository):
        payload = CloseCashRegisterSessionDTO(
            session_id=uuid4(),
            company_id=uuid4(),
            closed_by=uuid4(),
            closing_balance=Decimal('1'),
        )
        mock_repository.close_session.return_value = None

        assert await service.close_session(payload) is None
        mock_repository.close_session.assert_awaited_once_with(payload)

    async def test_list_recent_sessions_delegates(self, service, mock_repository):
        cid = uuid4()
        mock_repository.list_recent_sessions.return_value = []

        assert await service.list_recent_sessions(cid, 5) == []
        mock_repository.list_recent_sessions.assert_awaited_once_with(cid, 5)
