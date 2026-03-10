from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, Request, status

from src.interface.api.v1.dependencies.market_paid import MarketPaidControllerDep
from src.interface.api.v1.schema.market_paid import (
    MarketPaidCreateSchema,
    MarketPaidOutSchema,
    PreapprovalPlanSearchResponseSchema,
)

tags_metadata = {
    'name': 'Planos de assinatura (Mercado Pago)',
    'description': 'Modulo de Mercado Pago',
}

router = APIRouter(
    prefix='/market-paid',
    tags=[tags_metadata['name']],
)


@router.get(
    '/preapproval-plans',
    description='Lista planos de assinatura (preapproval_plan) do Mercado Pago',
    status_code=status.HTTP_200_OK,
    response_model=PreapprovalPlanSearchResponseSchema,
)
async def search_preapproval_plans(
    request: Request,
    controller: MarketPaidControllerDep,
    offset: int = Query(0, ge=0, description='Offset da paginação'),
    limit: int = Query(10, ge=1, le=30, description='Limite por página'),
    company_id: UUID | None = Query(
        None, description='ID da empresa (opcional, alternativa ao header)'
    ),
    x_company_id: UUID | None = Header(
        None, alias='x-company-id', description='ID da empresa via header'
    ),
) -> PreapprovalPlanSearchResponseSchema:
    resolved_company_id = (
        company_id or x_company_id or getattr(request.state, 'company_id', None)
    )
    if resolved_company_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail='Informe o company_id via query, header x-company-id ou token',
        )

    return await controller.search_preapproval_plans(
        company_id=resolved_company_id,
        offset=offset,
        limit=limit,
    )


@router.post(
    '',
    description='Criar as variáveis de ambiente do Mercado Pago',
    status_code=status.HTTP_201_CREATED,
    response_model=MarketPaidOutSchema,
)
async def create_market_paid(
    controller: MarketPaidControllerDep,
    market_paid: MarketPaidCreateSchema,
) -> MarketPaidOutSchema:
    return await controller.create_market_paid(market_paid)


@router.get(
    '/{id}',
    description='Buscar uma variável de ambiente do Mercado Pago',
    status_code=status.HTTP_200_OK,
    response_model=MarketPaidOutSchema,
)
async def get_market_paid(
    controller: MarketPaidControllerDep,
    id: UUID,
) -> MarketPaidOutSchema:
    return await controller.get_market_paid(id)
