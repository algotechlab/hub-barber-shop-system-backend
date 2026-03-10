from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MarketPaidCreateDTO(BaseModel):
    company_id: UUID
    public_key: str
    access_token: str
    market_paid_acess_token: str
    client_id: str
    client_secret: str


class MarketPaidOutDTO(MarketPaidCreateDTO):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool


class MarketPaidAuthTokenDTO(BaseModel):
    client_secret: str
    client_id: str
    grant_type: str
    code: str
    code_verifier: str
    redirect_uri: str
    refresh_token: str
    test_token: str


class MarketPaidAuthTokenResponseDTO(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: str
    refresh_token: str
    test_token: str


# DTOs para resposta da API de planos de assinatura (preapproval_plan/search)


class AutoRecurringDTO(BaseModel):
    """Recorrência automática do plano de assinatura."""

    frequency: int
    currency_id: str
    transaction_amount: float
    frequency_type: str  # "months" | "days"
    billing_day: Optional[int] = None  # presente quando frequency_type = "months"
    repetitions: Optional[int] = (
        None  # opcional, para planos com número limitado de cobranças
    )


class PreapprovalPlanItemDTO(BaseModel):
    """Item de plano de assinatura retornado pela API Mercado Pago."""

    id: str
    reason: str
    status: str  # "active" | "cancelled" | etc.
    subscribed: int
    back_url: str
    auto_recurring: AutoRecurringDTO
    collector_id: int
    init_point: str
    date_created: str
    last_modified: str
    external_reference: str = ''
    application_id: int


class PagingDTO(BaseModel):
    """Paginação da resposta da API."""

    offset: int
    limit: int
    total: int


class PreapprovalPlanSearchResponseDTO(BaseModel):
    """Resposta da API GET /preapproval_plan/search."""

    paging: PagingDTO
    results: list[PreapprovalPlanItemDTO] = Field(default_factory=list)
