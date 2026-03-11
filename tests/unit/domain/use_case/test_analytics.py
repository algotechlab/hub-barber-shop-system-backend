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
)
from src.domain.use_case.analytics import AnalyticsUseCase

pytestmark = pytest.mark.unit


def _build_metrics() -> DashboardMetricsDTO:
    return DashboardMetricsDTO(
        resumo_mes=MonthlySummaryDTO(
            faturamento_bruto=Decimal('1800.00'),
            despesas=Decimal('600.00'),
            lucro=Decimal('1200.00'),
            margem_percentual=66.67,
            total_atendimentos=30,
            clientes_distintos=22,
            ticket_medio_atendimento=Decimal('60.00'),
            ticket_medio_cliente=Decimal('81.82'),
            clientes_novos_periodo=9,
            taxa_retorno_percentual=45.45,
            atendimentos_por_dia=5.0,
        ),
        ranking_barbeiros=[
            BarberRankingItemDTO(
                employee_id=uuid4(),
                employee_name='Henrique',
                faturamento=Decimal('900.00'),
                atendimentos=15,
                clientes_distintos=12,
                ticket_medio_atendimento=Decimal('60.00'),
                ticket_medio_cliente=Decimal('75.00'),
                clientes_novos=4,
                taxa_retorno_percentual=50.0,
                frequencia_media_clientes=1.25,
            )
        ],
        indicadores_clientes=CustomerMetricsDTO(
            clientes_distintos=22,
            clientes_novos=9,
            clientes_recorrentes=13,
            frequencia_media=1.36,
            clientes_nunca_voltaram=6,
            taxa_retorno_percentual=59.09,
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
