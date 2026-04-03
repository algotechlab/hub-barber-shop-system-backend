from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Query, Request, status

from src.domain.service.marketing import MarketingService
from src.domain.use_case.marketing import MarketingUseCase
from src.infrastructure.external_apis.evolution_api import EvolutionApi
from src.infrastructure.repositories.marketing_inactive_postgres import (
    MarketingInactiveRepositoryPostgres,
)
from src.infrastructure.repositories.template_marketing_postgres import (
    TemplateMarketingRepositoryPostgres,
)
from src.interface.api.v1.controller.marketing import MarketingController
from src.interface.api.v1.dependencies.common.session import VerifiedSessionDep


async def resolve_marketing_company_id(
    request: Request,
    company_id: UUID | None = Query(
        None, description='Obrigatório para token owner (sem company no JWT)'
    ),
    x_company_id: UUID | None = Header(
        None,
        alias='x-company-id',
        description='Alternativa ao query company_id para owner',
    ),
) -> UUID:
    token_company = getattr(request.state, 'company_id', None)
    if token_company is not None:
        return token_company
    resolved = company_id or x_company_id
    if resolved is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                'Informe company_id (query ou header x-company-id) para token owner.'
            ),
        )
    return resolved


MarketingCompanyIdDep = Annotated[UUID, Depends(resolve_marketing_company_id)]


async def get_marketing_controller(
    session: VerifiedSessionDep,
) -> MarketingController:
    template_repo = TemplateMarketingRepositoryPostgres(session)
    inactive_repo = MarketingInactiveRepositoryPostgres(session)
    evolution = EvolutionApi()
    marketing_service = MarketingService(template_repo, evolution, inactive_repo)
    use_case = MarketingUseCase(marketing_service)
    return MarketingController(use_case)


MarketingControllerDep = Annotated[
    MarketingController, Depends(get_marketing_controller)
]
