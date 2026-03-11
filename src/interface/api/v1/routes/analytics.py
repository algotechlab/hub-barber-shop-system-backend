from fastapi import APIRouter, Depends, Request, status

from src.interface.api.v1.dependencies.analytics import AnalyticsRepositoryDep
from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee_or_owner,
)
from src.interface.api.v1.schema.analytics import (
    DashboardFilterInSchema,
    DashboardMetricsOutSchema,
)

tags_metadata = {
    'name': 'Analytics',
    'description': ('Modulo de indicadores financeiros e operacionais.'),
}

router = APIRouter(
    prefix='/analytics',
    tags=[tags_metadata['name']],
    dependencies=[Depends(require_current_employee_or_owner)],
)


@router.get(
    '/dashboard',
    description='Rota para obter os indicadores do painel de gestão',
    status_code=status.HTTP_200_OK,
    response_model=DashboardMetricsOutSchema,
)
async def get_dashboard_metrics(
    controller: AnalyticsRepositoryDep,
    request: Request,
    dashboard_filter: DashboardFilterInSchema = Depends(),
) -> DashboardMetricsOutSchema:
    return await controller.get_dashboard_metrics(
        dashboard_filter, company_id=request.state.company_id
    )
