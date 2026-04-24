from fastapi import APIRouter, Depends, Request, status

from src.interface.api.v1.dependencies.common.auth import require_current_user
from src.interface.api.v1.dependencies.common.pagination import PaginationParamsDep
from src.interface.api.v1.dependencies.user_subscription import (
    UserSubscriptionControllerDep,
)
from src.interface.api.v1.schema.user_subscription import (
    CreateUserSubscriptionSchema,
    UserSubscriptionOutSchema,
    UserSubscriptionWithPlanOutSchema,
)

tags_metadata = {
    'name': 'Assinaturas do cliente',
    'description': 'Adesão e listagem das assinaturas do usuário autenticado.',
}

router = APIRouter(
    prefix='/user-subscriptions',
    tags=[tags_metadata['name']],
    dependencies=[Depends(require_current_user)],
)


@router.post(
    '',
    description=(
        'Solicita adesão a um plano ativo: cria registro em PENDING_PAYMENT até o '
        'funcionário confirmar o pagamento em activate-after-payment'
    ),
    status_code=status.HTTP_201_CREATED,
    response_model=UserSubscriptionOutSchema,
)
async def create_user_subscription(
    controller: UserSubscriptionControllerDep,
    body: CreateUserSubscriptionSchema,
    request: Request,
) -> UserSubscriptionOutSchema:
    return await controller.create(
        body,
        company_id=request.state.company_id,
        user_id=request.state.user_id,
    )


@router.get(
    '/me',
    description='Lista assinaturas do usuário autenticado (com dados do plano)',
    status_code=status.HTTP_200_OK,
    response_model=list[UserSubscriptionWithPlanOutSchema],
)
async def list_my_subscriptions(
    controller: UserSubscriptionControllerDep,
    pagination: PaginationParamsDep,
    request: Request,
) -> list[UserSubscriptionWithPlanOutSchema]:
    return await controller.list_mine(
        pagination,
        company_id=request.state.company_id,
        user_id=request.state.user_id,
    )
