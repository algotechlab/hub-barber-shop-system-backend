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
from src.domain.exceptions.cash_register import (
    CashRegisterNoOpenSessionException,
    CashRegisterOpenSessionExistsException,
    CashRegisterSessionAlreadyClosedException,
    CashRegisterSessionClosedException,
    CashRegisterSessionNotFoundException,
)
from src.domain.use_case.cash_register import CashRegisterUseCase
from src.infrastructure.database.models.commom.cash_movement_kind import (
    CashMovementKind,
)


@pytest.mark.unit
class TestCashRegisterUseCase:
    @pytest.fixture
    def mock_service(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_service):
        return CashRegisterUseCase(cash_register_service=mock_service)

    def _session(
        self,
        *,
        closed_at=None,
        session_id=None,
        company_id=None,
    ) -> CashRegisterSessionOutDTO:
        now = datetime.now(timezone.utc)
        return CashRegisterSessionOutDTO(
            id=session_id if session_id is not None else uuid4(),
            company_id=company_id if company_id is not None else uuid4(),
            opened_by=uuid4(),
            closed_by=None,
            opened_at=now,
            closed_at=closed_at,
            opening_balance=Decimal('100'),
            closing_balance=Decimal('100') if closed_at else None,
            expected_balance=Decimal('100') if closed_at else None,
            opening_notes=None,
            closing_notes=None,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )

    async def test_open_raises_when_already_open(self, use_case, mock_service):
        mock_service.get_open_session.return_value = self._session()
        payload = OpenCashRegisterSessionDTO(
            company_id=uuid4(),
            opened_by=uuid4(),
            opening_balance=Decimal('1'),
        )

        with pytest.raises(CashRegisterOpenSessionExistsException):
            await use_case.open_session(payload)

    async def test_open_calls_service_when_no_open_session(
        self, use_case, mock_service
    ):
        mock_service.get_open_session.return_value = None
        out = self._session()
        mock_service.open_session.return_value = out
        payload = OpenCashRegisterSessionDTO(
            company_id=uuid4(),
            opened_by=uuid4(),
            opening_balance=Decimal('1'),
        )

        result = await use_case.open_session(payload)

        assert result == out
        mock_service.open_session.assert_awaited_once_with(payload)

    async def test_close_raises_when_already_closed(self, use_case, mock_service):
        sid = uuid4()
        cid = uuid4()
        mock_service.get_session_by_id.return_value = self._session(
            closed_at=datetime.now(timezone.utc),
            session_id=sid,
            company_id=cid,
        )
        payload = CloseCashRegisterSessionDTO(
            session_id=sid,
            company_id=cid,
            closed_by=uuid4(),
            closing_balance=Decimal('1'),
        )

        with pytest.raises(CashRegisterSessionAlreadyClosedException):
            await use_case.close_session(payload)

    async def test_adjustment_raises_when_session_closed(self, use_case, mock_service):
        sid = uuid4()
        cid = uuid4()
        mock_service.get_session_by_id.return_value = self._session(
            closed_at=datetime.now(timezone.utc),
            session_id=sid,
            company_id=cid,
        )
        payload = CashRegisterAdjustmentCreateDTO(
            session_id=sid,
            company_id=cid,
            created_by=uuid4(),
            kind=CashMovementKind.supply,
            amount=Decimal('1'),
            description='x',
        )

        with pytest.raises(CashRegisterSessionClosedException):
            await use_case.register_adjustment(payload)

    async def test_adjustment_raises_when_session_missing(self, use_case, mock_service):
        mock_service.get_session_by_id.return_value = None
        payload = CashRegisterAdjustmentCreateDTO(
            session_id=uuid4(),
            company_id=uuid4(),
            created_by=uuid4(),
            kind=CashMovementKind.supply,
            amount=Decimal('1'),
            description='x',
        )

        with pytest.raises(CashRegisterSessionNotFoundException):
            await use_case.register_adjustment(payload)

    async def test_get_open_session_raises_when_none(self, use_case, mock_service):
        mock_service.get_open_session.return_value = None

        with pytest.raises(CashRegisterNoOpenSessionException):
            await use_case.get_open_session(uuid4())

    async def test_get_open_session_returns_session(self, use_case, mock_service):
        cid = uuid4()
        session = self._session(company_id=cid, closed_at=None)
        mock_service.get_open_session.return_value = session

        assert await use_case.get_open_session(cid) is session

    async def test_close_session_raises_when_session_missing_initially(
        self, use_case, mock_service
    ):
        mock_service.get_session_by_id.return_value = None
        payload = CloseCashRegisterSessionDTO(
            session_id=uuid4(),
            company_id=uuid4(),
            closed_by=uuid4(),
            closing_balance=Decimal('1'),
        )

        with pytest.raises(CashRegisterSessionNotFoundException):
            await use_case.close_session(payload)

    async def test_list_recent_sessions_delegates(self, use_case, mock_service):
        cid = uuid4()
        mock_service.list_recent_sessions.return_value = []

        assert await use_case.list_recent_sessions(cid, 15) == []
        mock_service.list_recent_sessions.assert_awaited_once_with(cid, 15)

    async def test_get_session_summary_raises_not_found(self, use_case, mock_service):
        mock_service.get_session_by_id.return_value = None

        with pytest.raises(CashRegisterSessionNotFoundException):
            await use_case.get_session_summary(uuid4(), uuid4())

    async def test_get_session_summary_returns(self, use_case, mock_service):
        sid = uuid4()
        cid = uuid4()
        session = self._session(session_id=sid, company_id=cid, closed_at=None)
        mock_service.get_session_by_id.return_value = session
        now = session.opened_at
        summary = CashRegisterSummaryDTO(
            session=session,
            sales_total=Decimal('0'),
            expenses_total=Decimal('0'),
            supplies_total=Decimal('0'),
            withdrawals_total=Decimal('0'),
            expected_balance=session.opening_balance,
            window_end_at=now,
        )
        mock_service.build_summary.return_value = summary

        result = await use_case.get_session_summary(sid, cid)

        assert result == summary
        mock_service.build_summary.assert_awaited_once()

    async def test_close_session_raises_when_repo_returns_none(
        self, use_case, mock_service
    ):
        sid = uuid4()
        cid = uuid4()
        eid = uuid4()
        mock_service.get_session_by_id.return_value = self._session(
            session_id=sid, company_id=cid, closed_at=None
        )
        mock_service.close_session.return_value = None
        payload = CloseCashRegisterSessionDTO(
            session_id=sid,
            company_id=cid,
            closed_by=eid,
            closing_balance=Decimal('1'),
        )

        with pytest.raises(CashRegisterSessionNotFoundException):
            await use_case.close_session(payload)

    async def test_close_session_returns_closed(self, use_case, mock_service):
        sid = uuid4()
        cid = uuid4()
        eid = uuid4()
        open_session = self._session(session_id=sid, company_id=cid, closed_at=None)
        closed_session = self._session(
            session_id=sid, company_id=cid, closed_at=open_session.opened_at
        )
        mock_service.get_session_by_id.return_value = open_session
        mock_service.close_session.return_value = closed_session
        payload = CloseCashRegisterSessionDTO(
            session_id=sid,
            company_id=cid,
            closed_by=eid,
            closing_balance=Decimal('10'),
        )

        result = await use_case.close_session(payload)

        assert result == closed_session

    async def test_register_adjustment_success(self, use_case, mock_service):
        sid = uuid4()
        cid = uuid4()
        session = self._session(session_id=sid, company_id=cid, closed_at=None)
        mock_service.get_session_by_id.return_value = session
        expected = AsyncMock()
        mock_service.create_adjustment.return_value = expected
        payload = CashRegisterAdjustmentCreateDTO(
            session_id=sid,
            company_id=cid,
            created_by=uuid4(),
            kind=CashMovementKind.supply,
            amount=Decimal('2'),
            description='ok',
        )

        result = await use_case.register_adjustment(payload)

        assert result == expected
