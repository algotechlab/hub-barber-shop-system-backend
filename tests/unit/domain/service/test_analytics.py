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
from src.domain.service.analytics import AnalyticsService

pytestmark = pytest.mark.unit


def _build_metrics() -> DashboardMetricsDTO:
    return DashboardMetricsDTO(
        monthly_summary=MonthlySummaryDTO(
            gross_revenue=Decimal('1000.00'),
            expenses=Decimal('300.00'),
            profit=Decimal('700.00'),
            margin_percent=70.0,
            total_appointments=20,
            distinct_customers=15,
            avg_ticket_per_appointment=Decimal('50.00'),
            avg_ticket_per_customer=Decimal('66.67'),
            new_customers_in_period=5,
            return_rate_percent=40.0,
            appointments_per_day=4.0,
        ),
        barber_ranking=[
            BarberRankingItemDTO(
                employee_id=uuid4(),
                employee_name='Hedris',
                revenue=Decimal('500.00'),
                appointments_count=10,
                distinct_customers=8,
                avg_ticket_per_appointment=Decimal('50.00'),
                avg_ticket_per_customer=Decimal('62.50'),
                new_customers=2,
                return_rate_percent=37.5,
                avg_customer_frequency=1.25,
            )
        ],
        service_ranking=[
            ServiceRankingItemDTO(
                service_id=uuid4(),
                service_name='Combo',
                appointments_count=5,
                revenue=Decimal('350.00'),
            )
        ],
        customer_metrics=CustomerMetricsDTO(
            distinct_customers=15,
            new_customers=5,
            returning_customers=10,
            avg_frequency=1.33,
            customers_never_returned=4,
            return_rate_percent=66.67,
        ),
    )


@pytest.mark.asyncio
async def test_analytics_service_delegates_to_repository():
    repository = AsyncMock()
    service = AnalyticsService(repository)
    dashboard_filter = DashboardFilterDTO(
        company_id=uuid4(),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        employee_id=None,
    )
    expected = _build_metrics()
    repository.get_dashboard_metrics.return_value = expected

    result = await service.get_dashboard_metrics(dashboard_filter)

    repository.get_dashboard_metrics.assert_awaited_once_with(dashboard_filter)
    assert result == expected
