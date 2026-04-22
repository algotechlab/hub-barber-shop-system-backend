from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.custom import DatabaseException
from src.domain.dtos.cash_register import (
    CashRegisterAdjustmentCreateDTO,
    CashRegisterAdjustmentOutDTO,
    CashRegisterSessionOutDTO,
    CashRegisterSummaryDTO,
    CloseCashRegisterSessionDTO,
    OpenCashRegisterSessionDTO,
)
from src.domain.exceptions.cash_register import CashRegisterOpenSessionExistsException
from src.domain.repositories.cash_register import CashRegisterRepository
from src.infrastructure.database.models.cash_register import (
    CashRegisterAdjustment,
    CashRegisterSession,
)
from src.infrastructure.database.models.commom.cash_movement_kind import (
    CashMovementKind,
)
from src.infrastructure.database.models.commom.payment_status import PaymentStatus
from src.infrastructure.database.models.expense import Expense
from src.infrastructure.database.models.schedule_finance import ScheduleFinance


def _money(value: object) -> Decimal:
    if value is None:
        return Decimal('0.00')
    d = value if isinstance(value, Decimal) else Decimal(str(value))
    return d.quantize(Decimal('0.01'))


class CashRegisterRepositoryPostgres(CashRegisterRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def open_session(
        self, payload: OpenCashRegisterSessionDTO
    ) -> CashRegisterSessionOutDTO:
        try:
            opened_at = datetime.now(timezone.utc)
            row = CashRegisterSession(
                company_id=payload.company_id,
                opened_by=payload.opened_by,
                opening_balance=payload.opening_balance,
                opening_notes=payload.opening_notes,
                opened_at=opened_at,
                is_deleted=False,
            )
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
            return CashRegisterSessionOutDTO.model_validate(row)
        except IntegrityError as err:
            await self.session.rollback()
            raise CashRegisterOpenSessionExistsException(
                'Já existe um caixa aberto para esta empresa.'
            ) from err
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_open_session(
        self, company_id: UUID
    ) -> Optional[CashRegisterSessionOutDTO]:
        try:
            stmt = select(CashRegisterSession).where(
                CashRegisterSession.company_id.__eq__(company_id),
                CashRegisterSession.closed_at.is_(None),
                CashRegisterSession.is_deleted.__eq__(False),
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                return None
            return CashRegisterSessionOutDTO.model_validate(row)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def get_session_by_id(
        self, session_id: UUID, company_id: UUID
    ) -> Optional[CashRegisterSessionOutDTO]:
        try:
            stmt = select(CashRegisterSession).where(
                CashRegisterSession.id.__eq__(session_id),
                CashRegisterSession.company_id.__eq__(company_id),
                CashRegisterSession.is_deleted.__eq__(False),
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                return None
            return CashRegisterSessionOutDTO.model_validate(row)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def _sum_sales(
        self,
        company_id: UUID,
        start_at: datetime,
        end_at: datetime,
    ) -> Decimal:
        paid_ts = func.coalesce(
            ScheduleFinance.paid_at,
            ScheduleFinance.created_at,
        )
        stmt = select(func.coalesce(func.sum(ScheduleFinance.amount_total), 0)).where(
            ScheduleFinance.company_id.__eq__(company_id),
            ScheduleFinance.is_deleted.__eq__(False),
            ScheduleFinance.payment_status.__eq__(PaymentStatus.paid),
            paid_ts.__ge__(start_at),
            paid_ts.__le__(end_at),
        )
        result = await self.session.execute(stmt)
        raw = result.scalar_one()
        return _money(raw)

    async def _sum_expenses(
        self,
        company_id: UUID,
        start_at: datetime,
        end_at: datetime,
    ) -> Decimal:
        stmt = select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.company_id.__eq__(company_id),
            Expense.is_deleted.__eq__(False),
            Expense.occurred_at.__ge__(start_at),
            Expense.occurred_at.__le__(end_at),
        )
        result = await self.session.execute(stmt)
        raw = result.scalar_one()
        return _money(raw)

    async def _sum_adjustments(
        self,
        session_id: UUID,
        kind: CashMovementKind,
    ) -> Decimal:
        stmt = select(func.coalesce(func.sum(CashRegisterAdjustment.amount), 0)).where(
            CashRegisterAdjustment.session_id.__eq__(session_id),
            CashRegisterAdjustment.is_deleted.__eq__(False),
            CashRegisterAdjustment.kind.__eq__(kind),
        )
        result = await self.session.execute(stmt)
        raw = result.scalar_one()
        return _money(raw)

    async def build_summary(
        self,
        session: CashRegisterSessionOutDTO,
        window_end_at: Optional[datetime],
    ) -> CashRegisterSummaryDTO:
        try:
            end = session.closed_at or window_end_at or datetime.now(timezone.utc)
            start = session.opened_at
            sales = await self._sum_sales(session.company_id, start, end)
            expenses = await self._sum_expenses(session.company_id, start, end)
            supplies = await self._sum_adjustments(session.id, CashMovementKind.supply)
            withdrawals = await self._sum_adjustments(
                session.id, CashMovementKind.withdrawal
            )
            expected = _money(session.opening_balance) + sales + supplies
            expected = expected - expenses - withdrawals
            return CashRegisterSummaryDTO(
                session=session,
                sales_total=sales,
                expenses_total=expenses,
                supplies_total=supplies,
                withdrawals_total=withdrawals,
                expected_balance=expected,
                window_end_at=end,
            )
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def close_session(
        self, payload: CloseCashRegisterSessionDTO
    ) -> Optional[CashRegisterSessionOutDTO]:
        try:
            session_row_result = await self.session.execute(
                select(CashRegisterSession).where(
                    CashRegisterSession.id.__eq__(payload.session_id),
                    CashRegisterSession.company_id.__eq__(payload.company_id),
                    CashRegisterSession.is_deleted.__eq__(False),
                )
            )
            session_row = session_row_result.scalar_one_or_none()
            if session_row is None or session_row.closed_at is not None:
                return None

            end_at = datetime.now(timezone.utc)
            session_dto = CashRegisterSessionOutDTO.model_validate(session_row)
            summary = await self.build_summary(session_dto, window_end_at=end_at)
            expected = summary.expected_balance

            stmt = (
                update(CashRegisterSession)
                .where(
                    CashRegisterSession.id.__eq__(payload.session_id),
                    CashRegisterSession.company_id.__eq__(payload.company_id),
                    CashRegisterSession.closed_at.is_(None),
                    CashRegisterSession.is_deleted.__eq__(False),
                )
                .values(
                    closed_at=end_at,
                    closed_by=payload.closed_by,
                    closing_balance=payload.closing_balance,
                    expected_balance=expected,
                    closing_notes=payload.closing_notes,
                )
                .returning(CashRegisterSession)
            )
            result = await self.session.execute(stmt)
            updated = result.scalar_one_or_none()
            if updated is None:
                await self.session.rollback()
                return None
            await self.session.commit()
            return CashRegisterSessionOutDTO.model_validate(updated)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def list_recent_sessions(
        self, company_id: UUID, limit: int = 30
    ) -> List[CashRegisterSessionOutDTO]:
        try:
            stmt = (
                select(CashRegisterSession)
                .where(
                    CashRegisterSession.company_id.__eq__(company_id),
                    CashRegisterSession.is_deleted.__eq__(False),
                )
                .order_by(CashRegisterSession.opened_at.desc())
                .limit(limit)
            )
            result = await self.session.execute(stmt)
            rows = result.scalars().all()
            return [CashRegisterSessionOutDTO.model_validate(row) for row in rows]
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))

    async def create_adjustment(
        self, payload: CashRegisterAdjustmentCreateDTO
    ) -> CashRegisterAdjustmentOutDTO:
        try:
            row = CashRegisterAdjustment(
                session_id=payload.session_id,
                company_id=payload.company_id,
                created_by=payload.created_by,
                kind=payload.kind,
                amount=payload.amount,
                description=payload.description,
                is_deleted=False,
            )
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
            return CashRegisterAdjustmentOutDTO.model_validate(row)
        except Exception as error:
            await self.session.rollback()
            raise DatabaseException(str(error))
