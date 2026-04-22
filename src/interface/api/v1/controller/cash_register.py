from decimal import Decimal
from typing import List
from uuid import UUID

from src.domain.dtos.cash_register import (
    CashRegisterAdjustmentCreateDTO,
    CashRegisterSummaryDTO,
    CloseCashRegisterSessionDTO,
    OpenCashRegisterSessionDTO,
)
from src.domain.use_case.cash_register import CashRegisterUseCase
from src.interface.api.v1.schema.cash_register import (
    CashRegisterAdjustmentCreateSchema,
    CashRegisterAdjustmentOutSchema,
    CashRegisterSessionOutSchema,
    CashRegisterSummaryOutSchema,
    CloseCashRegisterSchema,
    OpenCashRegisterSchema,
)


class CashRegisterController:
    def __init__(self, cash_register_use_case: CashRegisterUseCase):
        self.cash_register_use_case = cash_register_use_case

    @staticmethod
    def _summary_to_schema(
        summary: CashRegisterSummaryDTO,
    ) -> CashRegisterSummaryOutSchema:
        diff: Decimal | None = None
        if summary.session.closing_balance is not None:
            diff = summary.session.closing_balance - summary.expected_balance
        return CashRegisterSummaryOutSchema(
            session=CashRegisterSessionOutSchema(**summary.session.model_dump()),
            sales_total=summary.sales_total,
            expenses_total=summary.expenses_total,
            supplies_total=summary.supplies_total,
            withdrawals_total=summary.withdrawals_total,
            expected_balance=summary.expected_balance,
            window_end_at=summary.window_end_at,
            balance_difference=diff,
        )

    async def open_session(
        self,
        body: OpenCashRegisterSchema,
        company_id: UUID,
        opened_by: UUID,
    ) -> CashRegisterSessionOutSchema:
        dto = OpenCashRegisterSessionDTO(
            company_id=company_id,
            opened_by=opened_by,
            opening_balance=body.opening_balance,
            opening_notes=body.opening_notes,
        )
        out = await self.cash_register_use_case.open_session(dto)
        return CashRegisterSessionOutSchema(**out.model_dump())

    async def get_open_session(self, company_id: UUID) -> CashRegisterSessionOutSchema:
        out = await self.cash_register_use_case.get_open_session(company_id)
        return CashRegisterSessionOutSchema(**out.model_dump())

    async def get_open_summary(self, company_id: UUID) -> CashRegisterSummaryOutSchema:
        session = await self.cash_register_use_case.get_open_session(company_id)
        summary = await self.cash_register_use_case.get_session_summary(
            session.id, company_id
        )
        return self._summary_to_schema(summary)

    async def get_session_summary(
        self, session_id: UUID, company_id: UUID
    ) -> CashRegisterSummaryOutSchema:
        summary = await self.cash_register_use_case.get_session_summary(
            session_id, company_id
        )
        return self._summary_to_schema(summary)

    async def close_session(
        self,
        session_id: UUID,
        body: CloseCashRegisterSchema,
        company_id: UUID,
        closed_by: UUID,
    ) -> CashRegisterSessionOutSchema:
        dto = CloseCashRegisterSessionDTO(
            session_id=session_id,
            company_id=company_id,
            closed_by=closed_by,
            closing_balance=body.closing_balance,
            closing_notes=body.closing_notes,
        )
        out = await self.cash_register_use_case.close_session(dto)
        return CashRegisterSessionOutSchema(**out.model_dump())

    async def list_sessions(
        self, company_id: UUID, limit: int = 30
    ) -> List[CashRegisterSessionOutSchema]:
        rows = await self.cash_register_use_case.list_recent_sessions(company_id, limit)
        return [CashRegisterSessionOutSchema(**r.model_dump()) for r in rows]

    async def register_adjustment(
        self,
        session_id: UUID,
        body: CashRegisterAdjustmentCreateSchema,
        company_id: UUID,
        employee_id: UUID,
    ) -> CashRegisterAdjustmentOutSchema:
        dto = CashRegisterAdjustmentCreateDTO(
            session_id=session_id,
            company_id=company_id,
            created_by=employee_id,
            kind=body.kind,
            amount=body.amount,
            description=body.description,
        )
        out = await self.cash_register_use_case.register_adjustment(dto)
        return CashRegisterAdjustmentOutSchema(**out.model_dump())
