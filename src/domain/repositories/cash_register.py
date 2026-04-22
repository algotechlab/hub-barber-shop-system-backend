from abc import ABC
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


class CashRegisterRepository(ABC):
    async def open_session(
        self, payload: OpenCashRegisterSessionDTO
    ) -> CashRegisterSessionOutDTO: ...

    async def get_open_session(
        self, company_id: UUID
    ) -> Optional[CashRegisterSessionOutDTO]: ...

    async def get_session_by_id(
        self, session_id: UUID, company_id: UUID
    ) -> Optional[CashRegisterSessionOutDTO]: ...

    async def close_session(
        self, payload: CloseCashRegisterSessionDTO
    ) -> Optional[CashRegisterSessionOutDTO]: ...

    async def build_summary(
        self,
        session: CashRegisterSessionOutDTO,
        window_end_at: Optional[datetime],
    ) -> CashRegisterSummaryDTO: ...

    async def list_recent_sessions(
        self, company_id: UUID, limit: int = 30
    ) -> List[CashRegisterSessionOutDTO]: ...

    async def create_adjustment(
        self, payload: CashRegisterAdjustmentCreateDTO
    ) -> CashRegisterAdjustmentOutDTO: ...
