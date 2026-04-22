from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.domain.dtos.cash_register import (
    CashRegisterAdjustmentCreateDTO,
    CashRegisterAdjustmentOutDTO,
    CashRegisterSessionOutDTO,
    CashRegisterSummaryDTO,
    CloseCashRegisterSessionDTO,
    OpenCashRegisterSessionDTO,
)
from src.domain.repositories.cash_register import CashRegisterRepository


class CashRegisterService:
    def __init__(self, cash_register_repository: CashRegisterRepository):
        self.cash_register_repository = cash_register_repository

    async def open_session(
        self, payload: OpenCashRegisterSessionDTO
    ) -> CashRegisterSessionOutDTO:
        return await self.cash_register_repository.open_session(payload)

    async def get_open_session(
        self, company_id: UUID
    ) -> Optional[CashRegisterSessionOutDTO]:
        return await self.cash_register_repository.get_open_session(company_id)

    async def get_session_by_id(
        self, session_id: UUID, company_id: UUID
    ) -> Optional[CashRegisterSessionOutDTO]:
        return await self.cash_register_repository.get_session_by_id(
            session_id, company_id
        )

    async def close_session(
        self, payload: CloseCashRegisterSessionDTO
    ) -> Optional[CashRegisterSessionOutDTO]:
        return await self.cash_register_repository.close_session(payload)

    async def build_summary(
        self,
        session: CashRegisterSessionOutDTO,
        window_end_at: Optional[datetime] = None,
    ) -> CashRegisterSummaryDTO:
        return await self.cash_register_repository.build_summary(session, window_end_at)

    async def list_recent_sessions(
        self, company_id: UUID, limit: int = 30
    ) -> List[CashRegisterSessionOutDTO]:
        return await self.cash_register_repository.list_recent_sessions(
            company_id, limit
        )

    async def create_adjustment(
        self, payload: CashRegisterAdjustmentCreateDTO
    ) -> CashRegisterAdjustmentOutDTO:
        return await self.cash_register_repository.create_adjustment(payload)
