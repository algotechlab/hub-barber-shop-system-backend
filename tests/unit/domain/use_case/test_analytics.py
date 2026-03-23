from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.analytics import (
    BarberRankingItemDTO,
    CustomerMetricsDTO,
    DashboardFilterDTO,
    DashboardMetricsDTO,
    MonthlySummaryDTO,
    ServiceRankingItemDTO,
)
from src.domain.use_case.analytics import AnalyticsUseCase

pytestmark = pytest.mark.unit


def _build_metrics() -> DashboardMetricsDTO:
    return DashboardMetricsDTO(
        monthly_summary=MonthlySummaryDTO(
            gross_revenue=Decimal('1800.00'),
            expenses=Decimal('600.00'),
            profit=Decimal('1200.00'),
            margin_percent=66.67,
            total_appointments=30,
            distinct_customers=22,
            avg_ticket_per_appointment=Decimal('60.00'),
            avg_ticket_per_customer=Decimal('81.82'),
            new_customers_in_period=9,
            return_rate_percent=45.45,
            appointments_per_day=5.0,
        ),
        barber_ranking=[
            BarberRankingItemDTO(
                employee_id=uuid4(),
                employee_name='Henrique',
                revenue=Decimal('900.00'),
                appointments_count=15,
                distinct_customers=12,
                avg_ticket_per_appointment=Decimal('60.00'),
                avg_ticket_per_customer=Decimal('75.00'),
                new_customers=4,
                return_rate_percent=50.0,
                avg_customer_frequency=1.25,
            )
        ],
        service_ranking=[
            ServiceRankingItemDTO(
                service_id=uuid4(),
                service_name='Barba',
                appointments_count=8,
                revenue=Decimal('240.00'),
            )
        ],
        customer_metrics=CustomerMetricsDTO(
            distinct_customers=22,
            new_customers=9,
            returning_customers=13,
            avg_frequency=1.36,
            customers_never_returned=6,
            return_rate_percent=59.09,
        ),
    )


@pytest.mark.asyncio
async def test_analytics_use_case_delegates_to_service():
    service = AsyncMock()
    use_case = AnalyticsUseCase(service)
    dashboard_filter = DashboardFilterDTO(
        company_id=uuid4(),
        start_date=date(2026, 2, 1),
        end_date=date(2026, 2, 28),
        employee_id=uuid4(),
    )
    expected = _build_metrics()
    service.get_dashboard_metrics.return_value = expected

    result = await use_case.get_dashboard_metrics(dashboard_filter)

    service.get_dashboard_metrics.assert_awaited_once_with(dashboard_filter)
    assert result == expected
