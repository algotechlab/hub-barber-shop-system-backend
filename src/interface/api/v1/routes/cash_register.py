from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status

from src.interface.api.v1.dependencies.cash_register import CashRegisterControllerDep
from src.interface.api.v1.dependencies.common.auth import require_current_employee
from src.interface.api.v1.schema.cash_register import (
    CashRegisterAdjustmentCreateSchema,
    CashRegisterAdjustmentOutSchema,
    CashRegisterSessionOutSchema,
    CashRegisterSummaryOutSchema,
    CloseCashRegisterSchema,
    OpenCashRegisterSchema,
)

tags_metadata = {
    'name': 'Caixa (financeiro)',
    'description': (
        'Abertura e fechamento de caixa, resumo com entradas (agendamentos pagos) '
        'e saídas (despesas), além de suprimento e sangria manual.'
    ),
}

router = APIRouter(
    prefix='/cash-register',
    tags=[tags_metadata['name']],
    dependencies=[Depends(require_current_employee)],
)


@router.post(
    '/sessions',
    description='Abre um novo turno de caixa para a empresa',
    status_code=status.HTTP_201_CREATED,
    response_model=CashRegisterSessionOutSchema,
)
async def open_cash_register(
    controller: CashRegisterControllerDep,
    body: OpenCashRegisterSchema,
    request: Request,
) -> CashRegisterSessionOutSchema:
    return await controller.open_session(
        body,
        company_id=request.state.company_id,
        opened_by=request.state.employee_id,
    )


@router.get(
    '/sessions/open',
    description='Retorna o caixa aberto da empresa, se existir',
    status_code=status.HTTP_200_OK,
    response_model=CashRegisterSessionOutSchema,
)
async def get_open_cash_register(
    controller: CashRegisterControllerDep,
    request: Request,
) -> CashRegisterSessionOutSchema:
    return await controller.get_open_session(request.state.company_id)


@router.get(
    '/sessions/open/summary',
    description='Resumo financeiro do caixa aberto (vendas, despesas, ajustes)',
    status_code=status.HTTP_200_OK,
    response_model=CashRegisterSummaryOutSchema,
)
async def get_open_cash_register_summary(
    controller: CashRegisterControllerDep,
    request: Request,
) -> CashRegisterSummaryOutSchema:
    return await controller.get_open_summary(request.state.company_id)


@router.get(
    '/sessions',
    description='Lista os turnos de caixa recentes da empresa',
    status_code=status.HTTP_200_OK,
    response_model=List[CashRegisterSessionOutSchema],
)
async def list_cash_register_sessions(
    controller: CashRegisterControllerDep,
    request: Request,
    limit: int = Query(30, ge=1, le=100),
) -> List[CashRegisterSessionOutSchema]:
    return await controller.list_sessions(request.state.company_id, limit)


@router.get(
    '/sessions/{session_id}/summary',
    description='Resumo de um turno de caixa específico',
    status_code=status.HTTP_200_OK,
    response_model=CashRegisterSummaryOutSchema,
)
async def get_cash_register_session_summary(
    controller: CashRegisterControllerDep,
    session_id: UUID,
    request: Request,
) -> CashRegisterSummaryOutSchema:
    return await controller.get_session_summary(session_id, request.state.company_id)


@router.post(
    '/sessions/{session_id}/close',
    description='Fecha o turno de caixa informando o saldo contado',
    status_code=status.HTTP_200_OK,
    response_model=CashRegisterSessionOutSchema,
)
async def close_cash_register(
    controller: CashRegisterControllerDep,
    session_id: UUID,
    body: CloseCashRegisterSchema,
    request: Request,
) -> CashRegisterSessionOutSchema:
    return await controller.close_session(
        session_id,
        body,
        company_id=request.state.company_id,
        closed_by=request.state.employee_id,
    )


@router.post(
    '/sessions/{session_id}/adjustments',
    description='Registra suprimento (entrada) ou sangria (saída) no caixa aberto',
    status_code=status.HTTP_201_CREATED,
    response_model=CashRegisterAdjustmentOutSchema,
)
async def create_cash_adjustment(
    controller: CashRegisterControllerDep,
    session_id: UUID,
    body: CashRegisterAdjustmentCreateSchema,
    request: Request,
) -> CashRegisterAdjustmentOutSchema:
    return await controller.register_adjustment(
        session_id,
        body,
        company_id=request.state.company_id,
        employee_id=request.state.employee_id,
    )
