from typing import List
from uuid import UUID

from src.domain.dtos.cash_register import (
    CashRegisterAdjustmentCreateDTO,
    CashRegisterAdjustmentOutDTO,
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
from src.domain.service.cash_register import CashRegisterService


class CashRegisterUseCase:
    def __init__(self, cash_register_service: CashRegisterService):
        self.cash_register_service = cash_register_service

    async def open_session(
        self, payload: OpenCashRegisterSessionDTO
    ) -> CashRegisterSessionOutDTO:
        existing = await self.cash_register_service.get_open_session(payload.company_id)
        if existing is not None:
            raise CashRegisterOpenSessionExistsException(
                'Já existe um caixa aberto para esta empresa.'
            )
        return await self.cash_register_service.open_session(payload)

    async def get_open_session(self, company_id: UUID) -> CashRegisterSessionOutDTO:
        session = await self.cash_register_service.get_open_session(company_id)
        if session is None:
            raise CashRegisterNoOpenSessionException(
                'Não há caixa aberto para esta empresa.'
            )
        return session

    async def get_session_summary(
        self, session_id: UUID, company_id: UUID
    ) -> CashRegisterSummaryDTO:
        session = await self.cash_register_service.get_session_by_id(
            session_id, company_id
        )
        if session is None:
            raise CashRegisterSessionNotFoundException('Turno de caixa não encontrado.')
        return await self.cash_register_service.build_summary(session, None)

    async def close_session(
        self, payload: CloseCashRegisterSessionDTO
    ) -> CashRegisterSessionOutDTO:
        session = await self.cash_register_service.get_session_by_id(
            payload.session_id, payload.company_id
        )
        if session is None:
            raise CashRegisterSessionNotFoundException('Turno de caixa não encontrado.')
        if session.closed_at is not None:
            raise CashRegisterSessionAlreadyClosedException(
                'Este turno de caixa já está fechado.'
            )
        closed = await self.cash_register_service.close_session(payload)
        if closed is None:
            raise CashRegisterSessionNotFoundException(
                'Não foi possível fechar o caixa.'
            )
        return closed

    async def list_recent_sessions(
        self, company_id: UUID, limit: int = 30
    ) -> List[CashRegisterSessionOutDTO]:
        return await self.cash_register_service.list_recent_sessions(company_id, limit)

    async def register_adjustment(
        self, payload: CashRegisterAdjustmentCreateDTO
    ) -> CashRegisterAdjustmentOutDTO:
        session = await self.cash_register_service.get_session_by_id(
            payload.session_id, payload.company_id
        )
        if session is None:
            raise CashRegisterSessionNotFoundException('Turno de caixa não encontrado.')
        if session.closed_at is not None:
            raise CashRegisterSessionClosedException(
                'Não é possível lançar ajustes em um caixa fechado.'
            )
        return await self.cash_register_service.create_adjustment(payload)
