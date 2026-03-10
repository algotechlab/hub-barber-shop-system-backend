from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AutoRecurringSchema(BaseModel):
    frequency: int
    currency_id: str
    transaction_amount: float
    frequency_type: str
    billing_day: Optional[int] = None
    repetitions: Optional[int] = None


class PreapprovalPlanItemSchema(BaseModel):
    id: str
    reason: str
    status: str
    subscribed: int
    back_url: str
    auto_recurring: AutoRecurringSchema
    collector_id: int
    init_point: str
    date_created: str
    last_modified: str
    external_reference: str = ''
    application_id: int


class PagingSchema(BaseModel):
    offset: int
    limit: int
    total: int


class PreapprovalPlanSearchResponseSchema(BaseModel):
    paging: PagingSchema
    results: list[PreapprovalPlanItemSchema] = Field(default_factory=list)


class MarketPaidCreateSchema(BaseModel):
    company_id: UUID
    public_key: str
    access_token: str
    market_paid_acess_token: str
    client_id: str
    client_secret: str


class MarketPaidOutSchema(MarketPaidCreateSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
