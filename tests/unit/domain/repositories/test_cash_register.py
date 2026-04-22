from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from src.domain.dtos.cash_register import (
    CashRegisterAdjustmentCreateDTO,
    CashRegisterAdjustmentOutDTO,
    CashRegisterSessionOutDTO,
    CashRegisterSummaryDTO,
    CloseCashRegisterSessionDTO,
    OpenCashRegisterSessionDTO,
)
from src.domain.repositories.cash_register import CashRegisterRepository
from src.infrastructure.database.models.commom.cash_movement_kind import (
    CashMovementKind,
)


@pytest.mark.unit
class TestCashRegisterRepositoryContract:
    def test_repository_exposes_methods(self):
        assert hasattr(CashRegisterRepository, 'open_session')
        assert hasattr(CashRegisterRepository, 'get_open_session')
        assert hasattr(CashRegisterRepository, 'get_session_by_id')
        assert hasattr(CashRegisterRepository, 'close_session')
        assert hasattr(CashRegisterRepository, 'build_summary')
        assert hasattr(CashRegisterRepository, 'list_recent_sessions')
        assert hasattr(CashRegisterRepository, 'create_adjustment')

    async def test_concrete_repository_runs_through_flow(self):
        company_id = uuid4()
        emp_id = uuid4()
        session_id = uuid4()
        now = datetime.now(timezone.utc)

        class ConcreteCashRegisterRepository(CashRegisterRepository):
            async def open_session(
                self, payload: OpenCashRegisterSessionDTO
            ) -> CashRegisterSessionOutDTO:
                return CashRegisterSessionOutDTO(
                    id=session_id,
                    company_id=payload.company_id,
                    opened_by=payload.opened_by,
                    closed_by=None,
                    opened_at=now,
                    closed_at=None,
                    opening_balance=payload.opening_balance,
                    closing_balance=None,
                    expected_balance=None,
                    opening_notes=payload.opening_notes,
                    closing_notes=None,
                    created_at=now,
                    updated_at=now,
                    is_deleted=False,
                )

            async def get_open_session(
                self, company_id: UUID
            ) -> CashRegisterSessionOutDTO | None:
                return None

            async def get_session_by_id(
                self, session_id: UUID, company_id: UUID
            ) -> CashRegisterSessionOutDTO | None:
                return None

            async def close_session(
                self, payload: CloseCashRegisterSessionDTO
            ) -> CashRegisterSessionOutDTO | None:
                return None

            async def build_summary(
                self,
                session: CashRegisterSessionOutDTO,
                window_end_at,
            ) -> CashRegisterSummaryDTO:
                return CashRegisterSummaryDTO(
                    session=session,
                    sales_total=Decimal('0'),
                    expenses_total=Decimal('0'),
                    supplies_total=Decimal('0'),
                    withdrawals_total=Decimal('0'),
                    expected_balance=session.opening_balance,
                    window_end_at=session.opened_at,
                )

            async def list_recent_sessions(
                self, company_id: UUID, limit: int = 30
            ) -> list:
                return []

            async def create_adjustment(
                self, payload: CashRegisterAdjustmentCreateDTO
            ) -> CashRegisterAdjustmentOutDTO:
                return CashRegisterAdjustmentOutDTO(
                    id=uuid4(),
                    session_id=payload.session_id,
                    company_id=payload.company_id,
                    created_by=payload.created_by,
                    kind=payload.kind,
                    amount=payload.amount,
                    description=payload.description,
                    created_at=now,
                    updated_at=now,
                    is_deleted=False,
                )

        repo = ConcreteCashRegisterRepository()
        opened = await repo.open_session(
            OpenCashRegisterSessionDTO(
                company_id=company_id,
                opened_by=emp_id,
                opening_balance=Decimal('100.00'),
            )
        )
        assert opened.id == session_id
        adj = await repo.create_adjustment(
            CashRegisterAdjustmentCreateDTO(
                session_id=session_id,
                company_id=company_id,
                created_by=emp_id,
                kind=CashMovementKind.supply,
                amount=Decimal('10'),
                description='suprimento',
            )
        )
        assert adj.amount == Decimal('10')
