from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.infrastructure.database.models.commom.payment_method import PaymentMethod
from src.infrastructure.database.models.commom.payment_status import PaymentStatus


class CreateScheduleSchema(BaseModel):
    user_id: UUID
    service_id: UUID
    product_id: Optional[UUID] = None
    employee_id: UUID
    time_register: datetime
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None


class UpdateScheduleSchema(BaseModel):
    user_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    time_register: Optional[datetime] = None
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    is_confirmed: Optional[bool] = None
    is_canceled: Optional[bool] = None


class ScheduleOutSchema(BaseModel):
    id: UUID
    user_id: UUID
    service_id: UUID
    product_id: Optional[UUID] = None
    employee_id: UUID
    company_id: UUID
    time_register: datetime
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    is_canceled: bool
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    user_name: Optional[str] = None
    employee_name: Optional[str] = None
    service_name: Optional[str] = None
    product_name: Optional[str] = None
    schedule_duration_minutes: Optional[int] = None


class SlotsInSchema(BaseModel):
    employee_id: UUID
    work_start: datetime
    work_end: datetime
    slot_minutes: int = 30
    target_date: Optional[date] = None


class SlotOutSchema(BaseModel):
    id: UUID
    time_start: datetime
    time_end: datetime
    is_available: bool
    is_blocked: bool


class CloseScheduleSchema(BaseModel):
    amount_service: Decimal
    amount_product: Optional[Decimal] = None
    amount_discount: Optional[Decimal] = None
    amount_total: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    paid_at: Optional[datetime] = None


class ScheduleFinanceOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    schedule_id: UUID
    company_id: UUID
    created_by: UUID
    amount_service: Decimal
    amount_product: Optional[Decimal] = None
    amount_discount: Optional[Decimal] = None
    amount_total: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
