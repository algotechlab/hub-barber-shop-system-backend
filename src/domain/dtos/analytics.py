from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class DashboardFilterDTO(BaseModel):
    company_id: UUID
    start_date: date
    end_date: date
    employee_id: Optional[UUID] = None


class MonthlySummaryDTO(BaseModel):
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
    appointments_per_day: float


class BarberRankingItemDTO(BaseModel):
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


class ServiceRankingItemDTO(BaseModel):
    """Revenue per service, allocated by catalog price (same rule as schedule close)."""

    service_id: UUID
    service_name: str
    appointments_count: int
    revenue: Decimal


class CustomerMetricsDTO(BaseModel):
    distinct_customers: int
    new_customers: int
    returning_customers: int
    avg_frequency: float
    customers_never_returned: int
    return_rate_percent: float


class DashboardMetricsDTO(BaseModel):
    monthly_summary: MonthlySummaryDTO
    barber_ranking: List[BarberRankingItemDTO]
    service_ranking: List[ServiceRankingItemDTO]
    customer_metrics: CustomerMetricsDTO
