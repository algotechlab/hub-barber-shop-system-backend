from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status

from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee,
    require_current_employee_or_user,
)
from src.interface.api.v1.dependencies.common.pagination import PaginationParamsDep
from src.interface.api.v1.dependencies.subscription_plan import (
    SubscriptionPlanControllerDep,
)
from src.interface.api.v1.schema.subscription_plan import (
    CreateSubscriptionPlanSchema,
    SubscriptionPlanOutSchema,
    UpdateSubscriptionPlanSchema,
)

tags_metadata = {
    'name': 'Planos de assinatura',
    'description': 'CRUD dos planos ofertados pela empresa (catálogo).',
}

router = APIRouter(
    prefix='/subscription-plans',
    tags=[tags_metadata['name']],
    dependencies=[Depends(require_current_employee_or_user)],
)


def _active_only_for_current_actor(request: Request) -> bool:
    """Cliente só vê planos ativos; funcionário pode incluir inativos."""
    return not hasattr(request.state, 'employee_id')


@router.get(
    '',
    description='Lista planos de assinatura da empresa',
    status_code=status.HTTP_200_OK,
    response_model=list[SubscriptionPlanOutSchema],
)
async def list_subscription_plans(
    controller: SubscriptionPlanControllerDep,
    pagination: PaginationParamsDep,
    request: Request,
) -> list[SubscriptionPlanOutSchema]:
    active_only = _active_only_for_current_actor(request)
    return await controller.list_plans(
        pagination,
        company_id=request.state.company_id,
        active_only=active_only,
    )


@router.post(
    '',
    description='Cria plano de assinatura (somente funcionário)',
    status_code=status.HTTP_201_CREATED,
    response_model=SubscriptionPlanOutSchema,
    dependencies=[Depends(require_current_employee)],
)
async def create_subscription_plan(
    controller: SubscriptionPlanControllerDep,
    body: CreateSubscriptionPlanSchema,
    request: Request,
) -> SubscriptionPlanOutSchema:
    return await controller.create_plan(body, company_id=request.state.company_id)


@router.get(
    '/{plan_id}',
    description='Busca plano por id',
    status_code=status.HTTP_200_OK,
    response_model=SubscriptionPlanOutSchema,
)
async def get_subscription_plan(
    controller: SubscriptionPlanControllerDep,
    plan_id: UUID,
    request: Request,
) -> SubscriptionPlanOutSchema:
    active_only = _active_only_for_current_actor(request)
    return await controller.get_plan(
        plan_id,
        company_id=request.state.company_id,
        active_only=active_only,
    )


@router.patch(
    '/{plan_id}',
    description='Atualiza plano (somente funcionário)',
    status_code=status.HTTP_200_OK,
    response_model=SubscriptionPlanOutSchema,
    dependencies=[Depends(require_current_employee)],
)
async def update_subscription_plan(
    controller: SubscriptionPlanControllerDep,
    plan_id: UUID,
    body: UpdateSubscriptionPlanSchema,
    request: Request,
) -> SubscriptionPlanOutSchema:
    return await controller.update_plan(
        plan_id, body, company_id=request.state.company_id
    )


@router.delete(
    '/{plan_id}',
    description='Remove plano (soft delete, somente funcionário)',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_current_employee)],
)
async def delete_subscription_plan(
    controller: SubscriptionPlanControllerDep,
    plan_id: UUID,
    request: Request,
) -> Response:
    await controller.delete_plan(plan_id, company_id=request.state.company_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
