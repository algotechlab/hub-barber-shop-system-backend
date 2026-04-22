from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.infrastructure.database.models.commom.cash_movement_kind import (
    CashMovementKind,
)


class OpenCashRegisterSessionDTO(BaseModel):
    company_id: UUID
    opened_by: UUID
    opening_balance: Decimal = Field(ge=0)
    opening_notes: Optional[str] = None


class CloseCashRegisterSessionDTO(BaseModel):
    session_id: UUID
    company_id: UUID
    closed_by: UUID
    closing_balance: Decimal = Field(ge=0)
    closing_notes: Optional[str] = None


class CashRegisterSessionOutDTO(BaseModel):
    id: UUID
    company_id: UUID
    opened_by: UUID
    closed_by: Optional[UUID] = None
    opened_at: datetime
    closed_at: Optional[datetime] = None
    opening_balance: Decimal
    closing_balance: Optional[Decimal] = None
    expected_balance: Optional[Decimal] = None
    opening_notes: Optional[str] = None
    closing_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class CashRegisterSummaryDTO(BaseModel):
    session: CashRegisterSessionOutDTO
    sales_total: Decimal
    expenses_total: Decimal
    supplies_total: Decimal
    withdrawals_total: Decimal
    expected_balance: Decimal
    window_end_at: datetime


class CashRegisterAdjustmentCreateDTO(BaseModel):
    session_id: UUID
    company_id: UUID
    created_by: UUID
    kind: CashMovementKind
    amount: Decimal = Field(gt=0)
    description: str


class CashRegisterAdjustmentOutDTO(BaseModel):
    id: UUID
    session_id: UUID
    company_id: UUID
    created_by: UUID
    kind: CashMovementKind
    amount: Decimal
    description: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)
