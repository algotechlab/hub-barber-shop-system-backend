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
from src.interface.api.v1.controller.analytics import AnalyticsController
from src.interface.api.v1.schema.analytics import (
    DashboardFilterInSchema,
    DashboardMetricsOutSchema,
)


def _build_metrics() -> DashboardMetricsDTO:
    return DashboardMetricsDTO(
        monthly_summary=MonthlySummaryDTO(
            gross_revenue=Decimal('1200.00'),
            expenses=Decimal('400.00'),
            profit=Decimal('800.00'),
            margin_percent=66.67,
            total_appointments=24,
            distinct_customers=18,
            avg_ticket_per_appointment=Decimal('50.00'),
            avg_ticket_per_customer=Decimal('66.67'),
            new_customers_in_period=7,
            return_rate_percent=44.44,
            appointments_per_day=4.8,
        ),
        barber_ranking=[
            BarberRankingItemDTO(
                employee_id=uuid4(),
                employee_name='Nilson',
                revenue=Decimal('650.00'),
                appointments_count=12,
                distinct_customers=10,
                avg_ticket_per_appointment=Decimal('54.17'),
                avg_ticket_per_customer=Decimal('65.00'),
                new_customers=3,
                return_rate_percent=40.0,
                avg_customer_frequency=1.2,
            )
        ],
        service_ranking=[
            ServiceRankingItemDTO(
                service_id=uuid4(),
                service_name='Corte',
                appointments_count=10,
                revenue=Decimal('500.00'),
            )
        ],
        customer_metrics=CustomerMetricsDTO(
            distinct_customers=18,
            new_customers=7,
            returning_customers=11,
            avg_frequency=1.33,
            customers_never_returned=5,
            return_rate_percent=61.11,
        ),
    )


@pytest.mark.unit
class TestAnalyticsController:
    @pytest.fixture
    def use_case(self):
        return AsyncMock()

    @pytest.fixture
    def controller(self, use_case):
        return AnalyticsController(use_case)

    async def test_get_dashboard_metrics_converts_filter_and_returns_schema(
        self, controller, use_case
    ):
        company_id = uuid4()
        payload = DashboardFilterInSchema(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            employee_id=uuid4(),
        )
        use_case.get_dashboard_metrics.return_value = _build_metrics()

        result = await controller.get_dashboard_metrics(payload, company_id=company_id)

        use_case.get_dashboard_metrics.assert_awaited_once()
        sent_filter = use_case.get_dashboard_metrics.call_args[0][0]
        assert isinstance(sent_filter, DashboardFilterDTO)
        assert sent_filter.company_id == company_id
        assert sent_filter.start_date == payload.start_date
        assert sent_filter.end_date == payload.end_date
        assert sent_filter.employee_id == payload.employee_id
        assert isinstance(result, DashboardMetricsOutSchema)
