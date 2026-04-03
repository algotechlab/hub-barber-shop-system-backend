from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee_or_owner,
)
from src.interface.api.v1.dependencies.marketing import (
    MarketingCompanyIdDep,
    MarketingControllerDep,
)
from src.interface.api.v1.schema.marketing import (
    InactiveClientsOutSchema,
    MessageTemplateOutSchema,
    MessageTemplatePutSchema,
    SendMarketingMessageSchema,
    WhatsappConnectionOutSchema,
)

tags_metadata = {
    'name': 'Marketing',
    'description': (
        'Templates, WhatsApp (Evolution), clientes inativos e disparo de mensagens.'
    ),
}

router = APIRouter(
    prefix='/marketing',
    tags=[tags_metadata['name']],
    dependencies=[Depends(require_current_employee_or_owner)],
)


@router.get(
    '/message-template',
    status_code=status.HTTP_200_OK,
    response_model=MessageTemplateOutSchema,
)
async def get_message_template(
    controller: MarketingControllerDep,
    company_id: MarketingCompanyIdDep,
) -> MessageTemplateOutSchema:
    return await controller.get_message_template(company_id)


@router.put(
    '/message-template',
    status_code=status.HTTP_200_OK,
    response_model=MessageTemplateOutSchema,
)
async def put_message_template(
    controller: MarketingControllerDep,
    company_id: MarketingCompanyIdDep,
    body: MessageTemplatePutSchema,
) -> MessageTemplateOutSchema:
    return await controller.save_message_template(company_id, body)


@router.get(
    '/whatsapp/connection',
    status_code=status.HTTP_200_OK,
    response_model=WhatsappConnectionOutSchema,
)
async def get_whatsapp_connection(
    controller: MarketingControllerDep,
    company_id: MarketingCompanyIdDep,
) -> WhatsappConnectionOutSchema:
    return await controller.get_whatsapp_connection(company_id)


@router.get(
    '/inactive-clients',
    status_code=status.HTTP_200_OK,
    response_model=InactiveClientsOutSchema,
)
async def get_inactive_clients(
    controller: MarketingControllerDep,
    company_id: MarketingCompanyIdDep,
    email: str | None = Query(
        None,
        description='Filtra por e-mail (parcial, sem diferenciar maiúsculas)',
    ),
    min_days: int | None = Query(
        None,
        ge=0,
        description='Dias mínimos desde a última visita (inclusive)',
    ),
    max_days: int | None = Query(
        None,
        ge=0,
        description='Dias máximos desde a última visita (inclusive)',
    ),
    lookback_years: int = Query(
        2,
        ge=1,
        le=10,
        description='Período (em anos) para carregar agendamentos no retorno',
    ),
    schedules_limit: int = Query(
        3000,
        ge=1,
        le=10000,
        description='Teto de agendamentos retornados (mais recentes primeiro)',
    ),
) -> InactiveClientsOutSchema:
    if min_days is not None and max_days is not None and min_days > max_days:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail='min_days não pode ser maior que max_days.',
        )
    return await controller.get_inactive_clients(
        company_id,
        email=email,
        min_days=min_days,
        max_days=max_days,
        lookback_years=lookback_years,
        schedules_limit=schedules_limit,
    )


@router.post(
    '/send-message',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def send_marketing_message(
    controller: MarketingControllerDep,
    company_id: MarketingCompanyIdDep,
    body: SendMarketingMessageSchema,
) -> None:
    await controller.send_message(company_id, body.number, body.text)
