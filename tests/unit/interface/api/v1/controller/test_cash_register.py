from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.cash_register import (
    CashRegisterAdjustmentOutDTO,
    CashRegisterSessionOutDTO,
    CashRegisterSummaryDTO,
)
from src.infrastructure.database.models.commom.cash_movement_kind import (
    CashMovementKind,
)
from src.interface.api.v1.controller.cash_register import CashRegisterController
from src.interface.api.v1.schema.cash_register import (
    CashRegisterAdjustmentCreateSchema,
    CashRegisterSessionOutSchema,
    CashRegisterSummaryOutSchema,
    CloseCashRegisterSchema,
    OpenCashRegisterSchema,
)


@pytest.mark.unit
class TestCashRegisterController:
    @pytest.fixture
    def mock_use_case(self):
        return AsyncMock()

    @pytest.fixture
    def controller(self, mock_use_case):
        return CashRegisterController(cash_register_use_case=mock_use_case)

    async def test_open_session_maps_schema(self, controller, mock_use_case):
        company_id = uuid4()
        emp_id = uuid4()
        now = datetime.now(timezone.utc)
        dto = CashRegisterSessionOutDTO(
            id=uuid4(),
            company_id=company_id,
            opened_by=emp_id,
            closed_by=None,
            opened_at=now,
            closed_at=None,
            opening_balance=Decimal('50'),
            closing_balance=None,
            expected_balance=None,
            opening_notes=None,
            closing_notes=None,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )
        mock_use_case.open_session.return_value = dto
        body = OpenCashRegisterSchema(opening_balance=Decimal('50'))

        result = await controller.open_session(body, company_id, emp_id)

        assert isinstance(result, CashRegisterSessionOutSchema)
        assert result.opening_balance == Decimal('50')

    async def test_summary_sets_balance_difference_when_closed(
        self, controller, mock_use_case
    ):
        now = datetime.now(timezone.utc)
        session = CashRegisterSessionOutDTO(
            id=uuid4(),
            company_id=uuid4(),
            opened_by=uuid4(),
            closed_by=None,
            opened_at=now,
            closed_at=now,
            opening_balance=Decimal('0'),
            closing_balance=Decimal('100'),
            expected_balance=Decimal('95'),
            opening_notes=None,
            closing_notes=None,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )
        summary = CashRegisterSummaryDTO(
            session=session,
            sales_total=Decimal('95'),
            expenses_total=Decimal('0'),
            supplies_total=Decimal('0'),
            withdrawals_total=Decimal('0'),
            expected_balance=Decimal('95'),
            window_end_at=now,
        )
        schema = controller._summary_to_schema(summary)

        assert isinstance(schema, CashRegisterSummaryOutSchema)
        assert schema.balance_difference == Decimal('5')

    async def test_close_session_delegates(self, controller, mock_use_case):
        sid = uuid4()
        cid = uuid4()
        eid = uuid4()
        now = datetime.now(timezone.utc)
        dto = CashRegisterSessionOutDTO(
            id=sid,
            company_id=cid,
            opened_by=eid,
            closed_by=eid,
            opened_at=now,
            closed_at=now,
            opening_balance=Decimal('0'),
            closing_balance=Decimal('10'),
            expected_balance=Decimal('10'),
            opening_notes=None,
            closing_notes=None,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )
        mock_use_case.close_session.return_value = dto

        result = await controller.close_session(
            sid,
            CloseCashRegisterSchema(closing_balance=Decimal('10')),
            cid,
            eid,
        )

        assert result.closing_balance == Decimal('10')

    async def test_get_open_session_maps(self, controller, mock_use_case):
        dto = CashRegisterSessionOutDTO(
            id=uuid4(),
            company_id=uuid4(),
            opened_by=uuid4(),
            closed_by=None,
            opened_at=datetime.now(timezone.utc),
            closed_at=None,
            opening_balance=Decimal('1'),
            closing_balance=None,
            expected_balance=None,
            opening_notes=None,
            closing_notes=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_deleted=False,
        )
        mock_use_case.get_open_session.return_value = dto

        out = await controller.get_open_session(dto.company_id)

        assert out.id == dto.id

    async def test_get_open_summary(self, controller, mock_use_case):
        sid = uuid4()
        cid = uuid4()
        now = datetime.now(timezone.utc)
        session = CashRegisterSessionOutDTO(
            id=sid,
            company_id=cid,
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
        mock_use_case.get_open_session.return_value = session
        summary = CashRegisterSummaryDTO(
            session=session,
            sales_total=Decimal('5'),
            expenses_total=Decimal('0'),
            supplies_total=Decimal('0'),
            withdrawals_total=Decimal('0'),
            expected_balance=Decimal('5'),
            window_end_at=now,
        )
        mock_use_case.get_session_summary.return_value = summary

        result = await controller.get_open_summary(cid)

        assert result.sales_total == Decimal('5')
        mock_use_case.get_session_summary.assert_awaited_once_with(sid, cid)

    async def test_get_session_summary(self, controller, mock_use_case):
        sid = uuid4()
        cid = uuid4()
        now = datetime.now(timezone.utc)
        session = CashRegisterSessionOutDTO(
            id=sid,
            company_id=cid,
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
            sales_total=Decimal('0'),
            expenses_total=Decimal('0'),
            supplies_total=Decimal('0'),
            withdrawals_total=Decimal('0'),
            expected_balance=Decimal('0'),
            window_end_at=now,
        )
        mock_use_case.get_session_summary.return_value = summary

        await controller.get_session_summary(sid, cid)

        mock_use_case.get_session_summary.assert_awaited_once_with(sid, cid)

    async def test_list_sessions(self, controller, mock_use_case):
        mock_use_case.list_recent_sessions.return_value = []

        assert await controller.list_sessions(uuid4(), 10) == []

    async def test_register_adjustment(self, controller, mock_use_case):
        sid = uuid4()
        cid = uuid4()
        eid = uuid4()
        now = datetime.now(timezone.utc)
        dto = CashRegisterAdjustmentOutDTO(
            id=uuid4(),
            session_id=sid,
            company_id=cid,
            created_by=eid,
            kind=CashMovementKind.supply,
            amount=Decimal('3'),
            description='x',
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )
        mock_use_case.register_adjustment.return_value = dto

        result = await controller.register_adjustment(
            sid,
            CashRegisterAdjustmentCreateSchema(
                kind=CashMovementKind.supply,
                amount=Decimal('3'),
                description='x',
            ),
            cid,
            eid,
        )

        assert result.amount == Decimal('3')
