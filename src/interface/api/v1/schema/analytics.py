from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class DashboardFilterInSchema(BaseModel):
    start_date: date
    end_date: date
    employee_id: Optional[UUID] = None

    @model_validator(mode='after')
    def validate_period(self) -> 'DashboardFilterInSchema':
        if self.end_date < self.start_date:
            raise ValueError('end_date must be greater than or equal to start_date')
        return self


class MonthlySummaryOutSchema(BaseModel):
    gross_revenue: Decimal
    expenses: Decimal
    profit: Decimal
    margin_percent: float
    total_appointments: int
    distinct_customers: int
    avg_ticket_per_appointment: Decimal
    avg_ticket_per_customer: Decimal
    new_customers_in_period: int
    return_rate_percent: float
    appointments_per_day: float = Field(
        description='Total appointments divided by working days in the period'
    )


class BarberRankingItemOutSchema(BaseModel):
    employee_id: UUID
    employee_name: str
    revenue: Decimal
    appointments_count: int
    distinct_customers: int
    avg_ticket_per_appointment: Decimal
    avg_ticket_per_customer: Decimal
    new_customers: int
    return_rate_percent: float
    avg_customer_frequency: float


class ServiceRankingItemOutSchema(BaseModel):
    service_id: UUID
    service_name: str
    appointments_count: int
    revenue: Decimal


class CustomerMetricsOutSchema(BaseModel):
    distinct_customers: int
    new_customers: int
    returning_customers: int
    avg_frequency: float
    customers_never_returned: int
    return_rate_percent: float


class DashboardMetricsOutSchema(BaseModel):
    monthly_summary: MonthlySummaryOutSchema
    barber_ranking: List[BarberRankingItemOutSchema]
    service_ranking: List[ServiceRankingItemOutSchema]
    customer_metrics: CustomerMetricsOutSchema
