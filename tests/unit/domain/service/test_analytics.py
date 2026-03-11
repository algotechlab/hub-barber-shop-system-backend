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
from src.domain.service.analytics import AnalyticsService

pytestmark = pytest.mark.unit


def _build_metrics() -> DashboardMetricsDTO:
    return DashboardMetricsDTO(
        resumo_mes=MonthlySummaryDTO(
            faturamento_bruto=Decimal('1000.00'),
            despesas=Decimal('300.00'),
            lucro=Decimal('700.00'),
            margem_percentual=70.0,
            total_atendimentos=20,
            clientes_distintos=15,
            ticket_medio_atendimento=Decimal('50.00'),
            ticket_medio_cliente=Decimal('66.67'),
            clientes_novos_periodo=5,
            taxa_retorno_percentual=40.0,
            atendimentos_por_dia=4.0,
        ),
        ranking_barbeiros=[
            BarberRankingItemDTO(
                employee_id=uuid4(),
                employee_name='Hedris',
                faturamento=Decimal('500.00'),
                atendimentos=10,
                clientes_distintos=8,
                ticket_medio_atendimento=Decimal('50.00'),
                ticket_medio_cliente=Decimal('62.50'),
                clientes_novos=2,
                taxa_retorno_percentual=37.5,
                frequencia_media_clientes=1.25,
            )
        ],
        indicadores_clientes=CustomerMetricsDTO(
            clientes_distintos=15,
            clientes_novos=5,
            clientes_recorrentes=10,
            frequencia_media=1.33,
            clientes_nunca_voltaram=4,
            taxa_retorno_percentual=66.67,
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
