from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.infrastructure.database.models.commom.cash_movement_kind import (
    CashMovementKind,
)


class OpenCashRegisterSchema(BaseModel):
    opening_balance: Decimal = Field(ge=0)
    opening_notes: Optional[str] = None


class CloseCashRegisterSchema(BaseModel):
    closing_balance: Decimal = Field(ge=0)
    closing_notes: Optional[str] = None


class CashRegisterSessionOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class CashRegisterSummaryOutSchema(BaseModel):
    session: CashRegisterSessionOutSchema
    sales_total: Decimal
    expenses_total: Decimal
    supplies_total: Decimal
    withdrawals_total: Decimal
    expected_balance: Decimal
    window_end_at: datetime
    balance_difference: Optional[Decimal] = None


class CashRegisterAdjustmentCreateSchema(BaseModel):
    kind: CashMovementKind
    amount: Decimal = Field(gt=0)
    description: str


class CashRegisterAdjustmentOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
