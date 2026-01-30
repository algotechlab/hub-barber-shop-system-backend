from fastapi import APIRouter, Query, status

from src.interface.api.v1.dependencies.market_paid import MarketPaidControllerDep
from src.interface.api.v1.schema.market_paid import (
    PreapprovalPlanSearchResponseSchema,
)

router = APIRouter(
    prefix='/market-paid',
    tags=['market-paid'],
)


@router.get(
    '/preapproval-plans',
    description='Lista planos de assinatura (preapproval_plan) do Mercado Pago',
    status_code=status.HTTP_200_OK,
    response_model=PreapprovalPlanSearchResponseSchema,
)
async def search_preapproval_plans(
    controller: MarketPaidControllerDep,
    offset: int = Query(0, ge=0, description='Offset da paginação'),
    limit: int = Query(10, ge=1, le=30, description='Limite por página'),
) -> PreapprovalPlanSearchResponseSchema:
    return await controller.search_preapproval_plans(offset=offset, limit=limit)
