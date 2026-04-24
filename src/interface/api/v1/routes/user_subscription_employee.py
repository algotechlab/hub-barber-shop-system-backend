from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status

from src.interface.api.v1.dependencies.common.auth import require_current_employee
from src.interface.api.v1.dependencies.common.pagination import PaginationParamsDep
from src.interface.api.v1.dependencies.user_subscription import (
    UserSubscriptionControllerDep,
)
from src.interface.api.v1.schema.user_subscription import (
    ActivateUserSubscriptionAfterPaymentSchema,
    UserSubscriptionOutSchema,
    UserSubscriptionWithPlanAndClientOutSchema,
)

tags_metadata = {
    'name': 'Assinaturas do cliente — confirmação (funcionário)',
    'description': (
        'Solicitações aguardando pagamento e ativação da assinatura após confirmação.'
    ),
}

router = APIRouter(
    prefix='/user-subscriptions',
    tags=[tags_metadata['name']],
    dependencies=[Depends(require_current_employee)],
)


@router.get(
    '/pending',
    description=(
        'Lista pedidos de assinatura com status PENDING_PAYMENT da empresa '
        '(para conferência e ativação após pagamento)'
    ),
    status_code=status.HTTP_200_OK,
    response_model=list[UserSubscriptionWithPlanAndClientOutSchema],
)
async def list_pending_user_subscriptions(
    controller: UserSubscriptionControllerDep,
    pagination: PaginationParamsDep,
    request: Request,
    client_name: str | None = Query(
        default=None,
        description='Filtro opcional: parte do nome do cliente',
    ),
) -> list[UserSubscriptionWithPlanAndClientOutSchema]:
    return await controller.list_pending(
        pagination,
        company_id=request.state.company_id,
        client_name=client_name,
    )


@router.post(
    '/{subscription_id}/activate-after-payment',
    description=(
        'Confirma o pagamento e ativa a assinatura (status ACTIVE). '
        'Só aplica se o registro estiver em PENDING_PAYMENT.'
    ),
    status_code=status.HTTP_200_OK,
    response_model=UserSubscriptionOutSchema,
)
async def activate_user_subscription_after_payment(
    controller: UserSubscriptionControllerDep,
    subscription_id: UUID,
    body: ActivateUserSubscriptionAfterPaymentSchema,
    request: Request,
) -> UserSubscriptionOutSchema:
    return await controller.activate_after_payment(
        subscription_id,
        company_id=request.state.company_id,
        body=body,
    )
