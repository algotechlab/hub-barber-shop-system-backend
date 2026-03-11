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
from src.interface.api.v1.controller.analytics import AnalyticsController
from src.interface.api.v1.schema.analytics import (
    DashboardFilterInSchema,
    DashboardMetricsOutSchema,
)


def _build_metrics() -> DashboardMetricsDTO:
    return DashboardMetricsDTO(
        resumo_mes=MonthlySummaryDTO(
            faturamento_bruto=Decimal('1200.00'),
            despesas=Decimal('400.00'),
            lucro=Decimal('800.00'),
            margem_percentual=66.67,
            total_atendimentos=24,
            clientes_distintos=18,
            ticket_medio_atendimento=Decimal('50.00'),
            ticket_medio_cliente=Decimal('66.67'),
            clientes_novos_periodo=7,
            taxa_retorno_percentual=44.44,
            atendimentos_por_dia=4.8,
        ),
        ranking_barbeiros=[
            BarberRankingItemDTO(
                employee_id=uuid4(),
                employee_name='Nilson',
                faturamento=Decimal('650.00'),
                atendimentos=12,
                clientes_distintos=10,
                ticket_medio_atendimento=Decimal('54.17'),
                ticket_medio_cliente=Decimal('65.00'),
                clientes_novos=3,
                taxa_retorno_percentual=40.0,
                frequencia_media_clientes=1.2,
            )
        ],
        indicadores_clientes=CustomerMetricsDTO(
            clientes_distintos=18,
            clientes_novos=7,
            clientes_recorrentes=11,
            frequencia_media=1.33,
            clientes_nunca_voltaram=5,
            taxa_retorno_percentual=61.11,
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
