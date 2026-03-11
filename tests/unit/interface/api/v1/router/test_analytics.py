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
)
from src.main import app

URL_ANALYTICS_DASHBOARD = '/api/v1/analytics/dashboard'

STATUS_CODE_200 = 200
STATUS_CODE_422 = 422


def _build_dashboard_out() -> DashboardMetricsOutSchema:
    return DashboardMetricsOutSchema(
        resumo_mes=MonthlySummaryOutSchema(
            faturamento_bruto=Decimal('1000.00'),
            despesas=Decimal('350.00'),
            lucro=Decimal('650.00'),
            margem_percentual=65.0,
            total_atendimentos=20,
            clientes_distintos=14,
            ticket_medio_atendimento=Decimal('50.00'),
            ticket_medio_cliente=Decimal('71.43'),
            clientes_novos_periodo=5,
            taxa_retorno_percentual=42.86,
            atendimentos_por_dia=4.0,
        ),
        ranking_barbeiros=[
            BarberRankingItemOutSchema(
                employee_id=uuid.uuid4(),
                employee_name='Hedris',
                faturamento=Decimal('600.00'),
                atendimentos=12,
                clientes_distintos=9,
                ticket_medio_atendimento=Decimal('50.00'),
                ticket_medio_cliente=Decimal('66.67'),
                clientes_novos=3,
                taxa_retorno_percentual=44.44,
                frequencia_media_clientes=1.33,
            )
        ],
        indicadores_clientes=CustomerMetricsOutSchema(
            clientes_distintos=14,
            clientes_novos=5,
            clientes_recorrentes=9,
            frequencia_media=1.43,
            clientes_nunca_voltaram=4,
            taxa_retorno_percentual=64.29,
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
        assert 'resumo_mes' in payload
        assert 'ranking_barbeiros' in payload
        assert 'indicadores_clientes' in payload

    def test_get_dashboard_metrics_returns_422_when_missing_dates(
        self, client, override_dependency_analytics
    ):
        response = client.get(URL_ANALYTICS_DASHBOARD)
        assert response.status_code == STATUS_CODE_422, response.json()
