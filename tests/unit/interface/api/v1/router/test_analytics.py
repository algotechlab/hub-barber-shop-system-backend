import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from fastapi import Request
from src.interface.api.v1.controller.analytics import AnalyticsController
from src.interface.api.v1.dependencies.analytics import get_analytics_controller
from src.interface.api.v1.dependencies.common.auth import (
    require_current_employee_or_owner,
)
from src.interface.api.v1.schema.analytics import (
    BarberRankingItemOutSchema,
    CustomerMetricsOutSchema,
    DashboardMetricsOutSchema,
    MonthlySummaryOutSchema,
    ServiceRankingItemOutSchema,
)
from src.main import app

URL_ANALYTICS_DASHBOARD = '/api/v1/analytics/dashboard'

STATUS_CODE_200 = 200
STATUS_CODE_422 = 422


def _build_dashboard_out() -> DashboardMetricsOutSchema:
    return DashboardMetricsOutSchema(
        monthly_summary=MonthlySummaryOutSchema(
            gross_revenue=Decimal('1000.00'),
            expenses=Decimal('350.00'),
            profit=Decimal('650.00'),
            margin_percent=65.0,
            total_appointments=20,
            distinct_customers=14,
            avg_ticket_per_appointment=Decimal('50.00'),
            avg_ticket_per_customer=Decimal('71.43'),
            new_customers_in_period=5,
            return_rate_percent=42.86,
            appointments_per_day=4.0,
        ),
        barber_ranking=[
            BarberRankingItemOutSchema(
                employee_id=uuid.uuid4(),
                employee_name='Hedris',
                revenue=Decimal('600.00'),
                appointments_count=12,
                distinct_customers=9,
                avg_ticket_per_appointment=Decimal('50.00'),
                avg_ticket_per_customer=Decimal('66.67'),
                new_customers=3,
                return_rate_percent=44.44,
                avg_customer_frequency=1.33,
            )
        ],
        service_ranking=[
            ServiceRankingItemOutSchema(
                service_id=uuid.uuid4(),
                service_name='Corte',
                appointments_count=10,
                revenue=Decimal('400.00'),
            )
        ],
        customer_metrics=CustomerMetricsOutSchema(
            distinct_customers=14,
            new_customers=5,
            returning_customers=9,
            avg_frequency=1.43,
            customers_never_returned=4,
            return_rate_percent=64.29,
        ),
    )


def _install_overrides() -> AsyncMock:
    mock_controller = AsyncMock(spec=AnalyticsController)

    def override_analytics_controller():
        return mock_controller

    app.dependency_overrides[get_analytics_controller] = override_analytics_controller

    async def override_require_current_employee_or_owner(request: Request):
        request.state.company_id = uuid.uuid4()
        request.state.employee_id = uuid.uuid4()
        return request.state.employee_id

    app.dependency_overrides[require_current_employee_or_owner] = (
        override_require_current_employee_or_owner
    )
    return mock_controller


@pytest.fixture
def override_dependency_analytics():
    mock_controller = _install_overrides()
    yield mock_controller
    app.dependency_overrides.clear()


@pytest.mark.unit
class TestAnalyticsRoutes:
    def test_get_dashboard_metrics_returns_200(
        self, client, override_dependency_analytics
    ):
        override_dependency_analytics.get_dashboard_metrics.return_value = (
            _build_dashboard_out()
        )

        response = client.get(
            URL_ANALYTICS_DASHBOARD,
            params={
                'start_date': date(2026, 1, 1).isoformat(),
                'end_date': date(2026, 1, 31).isoformat(),
            },
        )

        assert response.status_code == STATUS_CODE_200, response.json()
        payload = response.json()
        assert 'monthly_summary' in payload
        assert 'barber_ranking' in payload
        assert 'service_ranking' in payload
        assert 'customer_metrics' in payload

    def test_get_dashboard_metrics_returns_422_when_missing_dates(
        self, client, override_dependency_analytics
    ):
        response = client.get(URL_ANALYTICS_DASHBOARD)
        assert response.status_code == STATUS_CODE_422, response.json()
